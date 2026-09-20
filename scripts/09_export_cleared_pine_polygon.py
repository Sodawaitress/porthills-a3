"""
US7 补充 - 把 cleared_pine 的真实多边形边界导出来，之前 06_cleared_pine_from_hansen.py
只用这个多边形(block_fc)画了张缩略图就丢掉了，没有存下来，导致 cleared_pine 一直
只有训练点、没有面。这次用**完全相同**的算法重新算一遍，这次真的导出。

⚠️ 核心参数跟 06_cleared_pine_from_hansen.py 完全一致，不能改，否则跟已有的28个
训练点对不上：
  - UMD/hansen/global_forest_change_2023_v1_11, lossyear == 16
  - connectedPixelCount >= 6 (约0.5ha)，8-连通

跑法：在已装好+认证过 earthengine-api 的机器上跑。
输出：scripts/cleared_pine_blocks.geojson (WGS84经纬度，导回本地后用arcpy投影成NZTM)
"""
import ee
import json

ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
MIN_PIX = 6  # 跟 06_cleared_pine_from_hansen.py 一致

loss16 = ee.Image('UMD/hansen/global_forest_change_2023_v1_11').select('lossyear').eq(16).clip(AOI)
size = loss16.selfMask().connectedPixelCount(maxSize=128, eightConnected=True)
blocks = loss16.selfMask().updateMask(size.gte(MIN_PIX))

block_fc = blocks.reduceToVectors(geometry=AOI, scale=30, geometryType='polygon',
                                   eightConnected=True, maxPixels=1e9)

n_blocks = block_fc.size().getInfo()
print('区块数量:', n_blocks)

result = block_fc.getInfo()

out_path = "cleared_pine_blocks.geojson"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f)
print('wrote ->', out_path)

# 顺手算一下总面积(用geodesic面积，避免投影误差)
total_area_m2 = block_fc.geometry().area(maxError=1).getInfo()
print('区块总面积:', round(total_area_m2 / 10000, 2), 'ha')
print('(跟旧的 24.58ha / 25ha 说法对比一下，不一定完全相等，因为旧数字来自亮度+绿度粗筛，'
      '不是Hansen方法算出来的 -- 两个数字不是同一个东西，不要混用)')
