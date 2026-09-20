"""
Python port of 06_hansen_loss_since_2017.js — run on the GEE-authenticated machine.
Hansen forest loss 2017-2023 (lossyear 17-23), same blocky filter as 2017 cleared_pine
(connectedPixelCount >= 6 @ 30m). Outputs polygons as geojson (drop into ArcGIS to
intersect with the Name_2012 Exotic Forest polygon) + prints area.
"""
import ee, json, os
ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "hansen_loss_2017_2023.geojson")
AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

lossyear = ee.Image('UMD/hansen/global_forest_change_2023_v1_11').select('lossyear').clip(AOI)
loss = lossyear.gte(17).And(lossyear.lte(23))                       # 2017-2023
size = loss.selfMask().connectedPixelCount(maxSize=128, eightConnected=True)
blocks = loss.selfMask().updateMask(size.gte(6))                    # blocky only

ha = (ee.Image.pixelArea().divide(10000).updateMask(blocks)
      .reduceRegion(reducer=ee.Reducer.sum(), geometry=AOI, scale=30, maxPixels=1e9)
      .get('area').getInfo())
print(f"blocky forest-loss 2017-2023 in AOI: {ha:.1f} ha")

fc = blocks.reduceToVectors(geometry=AOI, scale=30, geometryType='polygon',
                            eightConnected=True, maxPixels=1e9)
print("blocks:", fc.size().getInfo())
json.dump(fc.getInfo(), open(OUT, "w"))
print("wrote ->", os.path.normpath(OUT))
