"""
Full Python port of A1's PortHills_dNBR (00_A1_PortHills_dNBR.js) compute
steps (not just the visualisation) - to get the actual printed numbers
(offset, threshold T, commission error, unmapped refugia ha, etc.) that
only exist as GEE console output when the JS is run in the Code Editor.
Logic is a direct translation, not a redesign - see the JS for the "why"
comments on each step.

Run on the GEE-authenticated machine: python 26_A1_python_port_get_numbers.py

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee

ee.Initialize(project='genuine-hold-427410-f0')

# ---- 1. AOI ----
ASSET_ID = 'projects/genuine-hold-427410-f0/assets/Port_Hills_2017_Fire_Boundary'
raw = ee.FeatureCollection(ASSET_ID)
fireWithHoles = raw.filter(ee.Filter.eq('Type', 'Fire Boundary')).first().geometry()
unburntFC = raw.filter(ee.Filter.eq('Type', 'Unburnt'))
aoi = fireWithHoles.union(unburntFC.geometry(), 1)
wideFrame = aoi.buffer(4000)

ha = 10000
pixelArea = ee.Image.pixelArea()


def haIn(mask, geom=None):
    return (pixelArea.updateMask(mask).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=geom or aoi,
        scale=30, maxPixels=1e9).getNumber('area').divide(ha))


print("===== OFFICIAL MAP (ha) =====")
print("perimeter:", aoi.area(1).divide(ha).getInfo())
print("official unburnt:", unburntFC.geometry().area(1).divide(ha).getInfo())
print("official burned:", fireWithHoles.area(1).divide(ha).getInfo())

# ---- 2. study period ----
preStart, preEnd = '2016-12-01', '2017-02-11'
postStart, postEnd = '2017-02-24', '2017-03-30'
outputBands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
outputScale = 30

# ---- 3. terrain ----
dem = ee.Image('USGS/SRTMGL1_003').rename('elev')
slope = ee.Terrain.slope(dem).rename('slope')
firePct = terrain_pct = dem.addBands(slope).select(['elev', 'slope']).reduceRegion(
    reducer=ee.Reducer.percentile([2, 98]), geometry=aoi, scale=outputScale, maxPixels=1e9)

# ---- 4. Landsat + smart mask ----
def scaleSR(image):
    return ee.Image(image.select('SR_B.').multiply(0.0000275).add(-0.2)
                     .copyProperties(image, ['system:time_start']))


def maskL8clouds_QA(image):
    qa = image.select('QA_PIXEL')
    inFire = ee.Image.constant(1).clip(aoi).mask()
    bad = (qa.bitwiseAnd(1 << 3).neq(0)
           .Or(qa.bitwiseAnd(1 << 4).neq(0).And(inFire.Not())))
    return scaleSR(image).updateMask(bad.Not())


l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(wideFrame)
preCol = l8.filterDate(preStart, preEnd).map(maskL8clouds_QA)
postCol = l8.filterDate(postStart, postEnd).map(maskL8clouds_QA)
pre = preCol.select(outputBands).median().clip(wideFrame)
post = postCol.select(outputBands).median().clip(wideFrame)

both = pre.select('SR_B5').mask().And(post.select('SR_B5').mask())

print("\n===== COVERAGE =====")
print("pre-fire scenes:", preCol.size().getInfo())
print("post-fire scenes:", postCol.size().getInfo())
cov = haIn(both).getInfo()
print("dNBR computable (ha):", cov)
print("coverage %:", cov / 1758.88 * 100)
print("cloud gap (ha):", 1758.88 - cov)

# ---- 5. indices ----
nbrPre = pre.normalizedDifference(['SR_B5', 'SR_B7']).rename('NBR_pre')
nbrPost = post.normalizedDifference(['SR_B5', 'SR_B7']).rename('NBR_post')
dnbrRaw = nbrPre.subtract(nbrPost).multiply(1000).rename('dNBR')

ndviPre = pre.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
vegMask = ndviPre.gt(0.25)
valid = both.And(vegMask)

# ---- 6. offset correction ----
dw = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
      .filterDate('2016-12-01', '2017-02-12').filterBounds(wideFrame)
      .select('label').mode())
water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('max_extent').unmask(0)

ring = aoi.buffer(2000).difference(aoi.buffer(500), 1)

controlMask = (ee.Image.constant(1).clip(ring).mask()
               .And(dem.gte(ee.Number(firePct.get('elev_p2'))))
               .And(dem.lte(ee.Number(firePct.get('elev_p98'))))
               .And(slope.gte(ee.Number(firePct.get('slope_p2'))))
               .And(dw.eq(1).Or(dw.eq(2)).Or(dw.eq(5)))
               .And(dw.neq(4))
               .And(water.eq(0)).And(vegMask).selfMask())

ctrl = dnbrRaw.updateMask(controlMask).reduceRegion(
    reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), None, True),
    geometry=ring, scale=outputScale, maxPixels=1e9)

offset = ee.Number(ctrl.get('dNBR_mean'))
ctrlSD = ee.Number(ctrl.get('dNBR_stdDev'))
dnbr = dnbrRaw.subtract(offset).rename('dNBR')

print("\n===== OFFSET =====")
print("mean dNBR on unburned control (the offset):", offset.getInfo())
print("standard deviation:", ctrlSD.getInfo())
print("control area (ha):", haIn(controlMask, ring).getInfo())

# ---- 7. threshold ----
islCore = unburntFC.geometry()
islPct = dnbr.updateMask(valid).reduceRegion(
    reducer=ee.Reducer.percentile([50, 90, 95]), geometry=islCore,
    scale=outputScale, maxPixels=1e9)
T = ee.Number(islPct.get('dNBR_p90'))


def falsePositiveRate(t):
    return dnbr.gt(t).updateMask(controlMask).reduceRegion(
        reducer=ee.Reducer.mean(), geometry=ring,
        scale=outputScale, maxPixels=1e9).getNumber('dNBR')


print("\n===== THRESHOLD =====")
print("island dNBR p50/p90/p95:", [islPct.get('dNBR_p50').getInfo(),
                                     islPct.get('dNBR_p90').getInfo(),
                                     islPct.get('dNBR_p95').getInfo()])
print("T:", T.getInfo())
print("2 x control sd would give:", ctrlSD.multiply(2).getInfo())
print("commission error at T:", falsePositiveRate(T).getInfo())

# ---- 8. classify + measure ----
severity = (ee.Image(0)
            .where(dnbr.gt(T), 1)
            .where(dnbr.gt(270), 2)
            .where(dnbr.gt(660), 3)
            .updateMask(valid).rename('severity'))


def burnedHa(t):
    return haIn(valid.And(dnbr.gt(t)))


covered = haIn(valid).getInfo()
burned = burnedHa(T).getInfo()
unburned = haIn(valid.And(dnbr.lte(T))).getInfo()

print("\n===== AREAS (ha), covered ground only =====")
print("covered:", covered)
print("burned:", burned)
print("unburned:", unburned)
print("sensitivity T-50/T+50:", burnedHa(T.subtract(50)).getInfo(), burnedHa(T.add(50)).getInfo())
print("burned rate %:", burned / covered * 100)
print("scaled to the perimeter:", burned / covered * 1758.88)

inIslands = haIn(valid.And(dnbr.lte(T)), unburntFC.geometry()).getInfo()
print("\n===== UNMAPPED REFUGIA =====")
print("my unburned total:", unburned)
print("inside the two official islands:", inIslands)
print("NEW unmapped refugia (ha):", unburned - inIslands)
print("scaled to the perimeter:", (unburned - inIslands) / (covered / 1758.88))

print("\n===== VALIDATION (cross-check against PortHills2017_island_validation.csv) =====")
print("officially burned ground also called burned:",
      dnbr.gt(T).updateMask(valid).reduceRegion(
          reducer=ee.Reducer.mean(), geometry=fireWithHoles,
          scale=outputScale, maxPixels=1e9).get('dNBR').getInfo())
