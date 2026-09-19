"""
Detect pre-fire logging/harvest to validate pine / cleared_pine labels.
Harvest = abrupt large tree loss, easy to see in change detection.

Two views (both as thumbnail URLs, open in browser):
  1. Hansen Global Forest Change - forest LOSS by year (ready product, 30 m).
     Loss in 2014-2016 = harvested before the 2017 fire.
  2. Same-season NDVI difference (summer 2016 -> summer 2017 pre-fire).
     Big negative = vegetation lost over that year (harvest).

Run: python3 03_detect_prefire_harvest.py   (GEE, this machine)
"""
import ee
ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

# ── 1. Hansen forest loss (lossyear: 1..23 = 2001..2023) ──
gfc = ee.Image('UMD/hansen/global_forest_change_2023_v1_11').clip(AOI)
lossyear = gfc.select('lossyear')
# highlight losses in 2014-2016 (values 14-16), grey out the rest
recent = lossyear.updateMask(lossyear.gte(14).And(lossyear.lte(16)))
loss_url = recent.getThumbURL({
    'region': AOI, 'dimensions': 700,
    'min': 14, 'max': 16, 'palette': ['yellow', 'orange', 'red'],  # 2014,2015,2016
})
# how much loss per year in the AOI (pixel counts)
hist = lossyear.updateMask(lossyear.gt(0)).reduceRegion(
    reducer=ee.Reducer.frequencyHistogram(), geometry=AOI, scale=30, maxPixels=1e9)
print('森林损失像元数(按年, 14=2014...16=2016):', hist.getInfo())
print('Hansen 森林损失(2014-16 高亮) 缩略图:', loss_url)

# ── 2. Same-season NDVI difference (Landsat 8, summer 2016 vs 2017 pre-fire) ──
def l8_ndvi(start, end):
    def prep(img):
        qa = img.select('QA_PIXEL')
        cloud = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
        sr = img.select('SR_B.').multiply(0.0000275).add(-0.2)
        return sr.updateMask(cloud.Not())
    col = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(AOI).filterDate(start, end).map(prep).median())
    return col.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')

ndvi16 = l8_ndvi('2016-01-01', '2016-03-31')      # summer 2016
ndvi17 = l8_ndvi('2016-11-01', '2017-02-12')      # 2017 pre-fire
dndvi = ndvi17.subtract(ndvi16).clip(AOI)         # negative = veg loss
dndvi_url = dndvi.getThumbURL({
    'region': AOI, 'dimensions': 700,
    'min': -0.4, 'max': 0.4, 'palette': ['red', 'white', 'green'],  # red = loss
})
print('NDVI 差(2016->2017, 红=植被减少) 缩略图:', dndvi_url)
print('\n红色大块 = 火前被伐/清掉的地方。对照你的 pine / cleared_pine 点看对不对。')
