"""
Define cleared_pine sample points from Hansen 2016 forest-loss (blocky patches only).
Same-satellite basis (Landsat time-series); keeps only sizeable connected blocks
so scattered noise / soft cloud edges are dropped (harvest = geometric blocks).

Outputs:
  - A3/cleared_pine_candidates.csv           (lon, lat, FuelClass, class_id)  -> load in ArcGIS
  - A3/harvest_check/cleared_pine_blocks.png (2017 true colour + thin block outline + points)
Run: python3 06_cleared_pine_from_hansen.py   (GEE, this machine)
"""
import ee, csv, urllib.request
ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
CSV = "/Users/sodawaitress/Desktop/ERST619/A3/cleared_pine_candidates.csv"
PNG = "/Users/sodawaitress/Desktop/ERST619/A3/harvest_check/cleared_pine_blocks.png"
N   = 80          # candidate points to generate
MIN_PIX = 6       # keep connected blocks >= this many 30 m pixels (~0.5 ha)

# ── 1. Hansen 2016 loss, keep only blocky patches ──
loss16 = ee.Image('UMD/hansen/global_forest_change_2023_v1_11').select('lossyear').eq(16).clip(AOI)
size   = loss16.selfMask().connectedPixelCount(maxSize=128, eightConnected=True)
blocks = loss16.selfMask().updateMask(size.gte(MIN_PIX))    # 1 where blocky 2016 loss

# ── 2. sample points inside the blocks ──
cls = ee.Image(6).updateMask(blocks).rename('class_id').toInt()
pts = cls.stratifiedSample(numPoints=N, classBand='class_id', region=AOI,
                           scale=30, geometries=True, seed=1)
feats = pts.getInfo()['features']
with open(CSV, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['lon', 'lat', 'FuelClass', 'class_id'])
    for ft in feats:
        lon, lat = ft['geometry']['coordinates']
        w.writerow([f'{lon:.6f}', f'{lat:.6f}', 'cleared_pine', 6])
print(f'wrote {len(feats)} points -> {CSV}')

# ── 3. verification image: 2017 true colour + block outline + points ──
def l8_truecolor(start, end):
    def prep(img):
        qa = img.select('QA_PIXEL')
        cloud = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
        return img.select('SR_B.').multiply(0.0000275).add(-0.2).updateMask(cloud.Not())
    med = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(AOI).filterDate(start, end).map(prep).median())
    return med.select(['SR_B4', 'SR_B3', 'SR_B2']).visualize(min=0, max=0.30)

block_fc = blocks.reduceToVectors(geometry=AOI, scale=30, geometryType='polygon',
                                  eightConnected=True, maxPixels=1e9)
vis = (l8_truecolor('2016-11-01', '2017-02-12')
       .paint(block_fc, 'ffff00', 2)      # thin yellow block outline (no fill)
       .paint(pts, 'ff00ff', 3))          # magenta sample points
url = vis.getThumbURL({'region': AOI, 'dimensions': 900, 'format': 'png'})
urllib.request.urlretrieve(url, PNG)
print('verification image ->', PNG)
