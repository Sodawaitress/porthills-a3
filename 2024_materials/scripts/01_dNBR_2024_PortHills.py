"""
ERST619 Fire Assessment - Step 1: 2024 Port Hills fire boundary + unburned patches (dNBR)
Method: dNBR (differenced Normalized Burn Ratio) - Steps 1-6 of the 10-step workflow
Data:   Sentinel-2 Surface Reflectance (Harmonized)
Fire:   2024-02-14 (Worsleys Rd, western Port Hills); operations completed 2024-03-13

Author: Yu Zhou
"""

import ee

# ============================================================
# 0. Authenticate + initialize
# ============================================================
# ee.Authenticate()   # uncomment on the first run to authorise once
ee.Initialize(project='genuine-hold-427410-f0')


# ============================================================
# 1. Study area AOI (Step 2) - western Port Hills, covers Worsleys fire
#    [west, south, east, north]
# ============================================================
aoi = ee.Geometry.Rectangle([172.60, -43.72, 172.75, -43.64])


# ============================================================
# 2. Pre-fire / post-fire date windows (Step 4)
#    ~3 months each; pre = as close to ignition as possible,
#    post = shortly after the fire is out (2024-03-13), not too late (re-greening)
# ============================================================
pre_start,  pre_end  = '2023-11-14', '2024-02-13'   # pre-fire
post_start, post_end = '2024-03-14', '2024-05-14'   # after fire is out


# ============================================================
# 3. Cloud mask (Step 5) - use the Sentinel-2 SCL band
#    SCL classes: 3=cloud shadow 8=med cloud 9=high cloud 10=cirrus 11=snow
# ============================================================
def mask_s2(img):
    scl = img.select('SCL')
    mask = (scl.neq(3)
            .And(scl.neq(8))
            .And(scl.neq(9))
            .And(scl.neq(10))
            .And(scl.neq(11)))
    # S2 SR reflectance is a 0-10000 integer; divide by 10000 -> 0-1
    return img.updateMask(mask).divide(10000)


# ============================================================
# 4. Cloud-free median composite for a date window (Step 5)
#    filter by area + date + scene cloudiness -> mask clouds -> median -> clip
# ============================================================
def get_s2_composite(start, end):
    return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(aoi)
            .filterDate(start, end)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
            .map(mask_s2)
            .median()
            .clip(aoi))

pre_img  = get_s2_composite(pre_start,  pre_end)
post_img = get_s2_composite(post_start, post_end)


# ============================================================
# 5. NBR + dNBR (Step 6)
#    NBR = (NIR - SWIR2)/(NIR + SWIR2);  S2: NIR=B8, SWIR2=B12
#    dNBR = preNBR - postNBR  (burned areas lose NBR -> positive dNBR)
# ============================================================
def nbr(img):
    return img.normalizedDifference(['B8', 'B12']).rename('NBR')

pre_nbr  = nbr(pre_img)
post_nbr = nbr(post_img)

dnbr = pre_nbr.subtract(post_nbr).rename('dNBR')   # roughly -2 .. 2
dnbr_scaled = dnbr.multiply(1000).rename('dNBR')   # USGS convention x1000


# ============================================================
# 6. Burn severity classes (USGS thresholds, after x1000) (Step 3)
#    <100 = unburned/very low (incl. "unburned patches"), 100-270 low,
#    270-660 moderate, >660 high
# ============================================================
severity = (dnbr_scaled
            .where(dnbr_scaled.lt(100), 1)                              # unburned / refugia
            .where(dnbr_scaled.gte(100).And(dnbr_scaled.lt(270)), 2)    # low
            .where(dnbr_scaled.gte(270).And(dnbr_scaled.lt(660)), 3)    # moderate
            .where(dnbr_scaled.gte(660), 4)                             # high
            .rename('severity'))

# fire boundary = clear burn (dNBR >= 100); unburned patches = inside boundary with dNBR < 100
burned = dnbr_scaled.gte(100).selfMask().rename('burned')


# ============================================================
# 7. Visualisation (geemap) - view results in Jupyter/Colab
# ============================================================
try:
    import geemap.core as geemap
except ImportError:
    import geemap

m = geemap.Map()
m.centerObject(aoi, 13)

rgb_vis = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3}
m.add_layer(pre_img,  rgb_vis, 'Pre-fire true colour')
m.add_layer(post_img, rgb_vis, 'Post-fire true colour')

dnbr_vis = {'min': -500, 'max': 1000,
            'palette': ['0000ff', 'ffffff', 'ffff00', 'ff8000', 'ff0000']}
m.add_layer(dnbr_scaled, dnbr_vis, 'dNBR')

sev_vis = {'min': 1, 'max': 4,
           'palette': ['1a9850', 'ffffbf', 'fdae61', 'd73027']}
m.add_layer(severity, sev_vis, 'Burn severity')
m.add_layer(aoi, {}, 'AOI', False)
# display(m)   # uncomment inside a notebook


# ============================================================
# 8. (Optional) Export dNBR to Google Drive - Step 9 map/data output
# ============================================================
def export_dnbr():
    task = ee.batch.Export.image.toDrive(
        image=dnbr_scaled,
        description='PortHills_2024_dNBR',
        folder='ERST619_Fire',
        fileNamePrefix='PortHills_2024_dNBR',
        region=aoi,
        scale=10,
        crs='EPSG:2193',           # NZTM2000, official NZ projection
        maxPixels=1e9)
    task.start()
    print('Export task started; check progress with task.status()')
    return task

# task = export_dnbr()   # uncomment when you want to export
