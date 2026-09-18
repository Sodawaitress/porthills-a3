"""
A3 · 点表引擎 (the foundation of §3 §4 §5)
================================================
做什么：火前 Landsat 8 → 缩放 → 云掩膜 → 合成 → 算指数 → 加地形 → 叠成特征栈
        → 在训练/验证点上采样 → 导出一张 CSV 点表。
这张表 = §3 数据探索 / §4 回归 / §5 分类 的共同输入。

跑法：GEE Python（Colab 里 `import ee; ee.Authenticate()` 一次即可），
      或把逻辑照搬到 JS Code Editor。

★ 你只需要改 3 个地方（下面标了 ← 改这里）。其余我讲清了为什么。
"""

import ee
ee.Initialize()

# ───────────────────────────────────────────────────────────
# 0. 研究区 + 时间窗
# ───────────────────────────────────────────────────────────
# western Port Hills AOI（A2 用的框；量算/导出用 NZTM EPSG:2193）
AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

# 火前窗口：2017 火起于 2017-02-13。取火前几个月做 median 合成，
# 既避开火、又多几景压掉云。★为什么用火前：烧掉处看不到原植被。
PRE_START = '2016-10-01'
PRE_END   = '2017-02-12'

# ───────────────────────────────────────────────────────────
# 1. 云/影掩膜 + 缩放（Landsat 8 C2L2）
# ───────────────────────────────────────────────────────────
def mask_and_scale(img):
    qa = img.select('QA_PIXEL')
    # QA_PIXEL 位：1 膨胀云, 2 卷云, 3 云, 4 云影 —— 任一为真就剔除
    cloud = (qa.bitwiseAnd(1 << 1)
               .Or(qa.bitwiseAnd(1 << 2))
               .Or(qa.bitwiseAnd(1 << 3))
               .Or(qa.bitwiseAnd(1 << 4)))
    # ★缩放系数：漏了后面全错。SR = DN × 0.0000275 − 0.2
    sr = img.select('SR_B.').multiply(0.0000275).add(-0.2)
    return (img.addBands(sr, None, True)
               .updateMask(cloud.Not())
               .copyProperties(img, ['system:time_start']))

l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(AOI)
        .filterDate(PRE_START, PRE_END)
        .map(mask_and_scale))

pre = l8.median().clip(AOI)            # 火前 median 合成

# 波段改名：SR_B2..B7 → B2..B7（后面好读、好对 lab 术语）
pre = pre.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
                 ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'])

# ───────────────────────────────────────────────────────────
# 2. 光谱指数（每个都要在报告里引用）
# ───────────────────────────────────────────────────────────
ndvi = pre.normalizedDifference(['B5', 'B4']).rename('NDVI')   # Rouse 1974
nbr  = pre.normalizedDifference(['B5', 'B7']).rename('NBR')    # Key&Benson 2006
ndwi = pre.normalizedDifference(['B3', 'B5']).rename('NDWI')   # McFeeters 1996
# BSI 裸土指数 = ((B6+B4)-(B5+B2)) / ((B6+B4)+(B5+B2))
bsi = pre.expression(
    '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))',
    {'SWIR': pre.select('B6'), 'RED': pre.select('B4'),
     'NIR':  pre.select('B5'), 'BLUE': pre.select('B2')}).rename('BSI')
# ⚠️ NDRE 需要 red-edge，Landsat 8 没有 → 只能等 Sentinel-2（A4 加）

# ───────────────────────────────────────────────────────────
# 3. 地形 correlates（landscape correlates，Christ et al. 2025 那套）
# ───────────────────────────────────────────────────────────
dem = ee.Image('USGS/SRTMGL1_003').clip(AOI)   # ← 换成 LINZ 8m DEM 更准（若已上传为 asset）
terrain = ee.Terrain.products(dem)             # elevation, slope, aspect
terr = terrain.select(['elevation', 'slope', 'aspect'])
# TWI / TRI / solar 可后加（先跑通核心，别一次背太多）

# ───────────────────────────────────────────────────────────
# 4. 特征栈（bands + indices + terrain）
# ───────────────────────────────────────────────────────────
stack = pre.addBands([ndvi, nbr, ndwi, bsi, terr])

# ───────────────────────────────────────────────────────────
# 5. 训练/验证点 → 采样成点表
# ───────────────────────────────────────────────────────────
# ★ 换成你的点：Collect Earth Online 导出后上传为 GEE asset，
#   或先用 LCDB 上传的 asset。属性里要有一列类别标签，名叫 'class'（整数）。
points = ee.FeatureCollection('users/你的用户名/porthills_training_points')  # ← 改这里

table = stack.sampleRegions(
    collection=points,
    properties=['class'],   # 保留类别标签
    scale=30,               # L8 原生分辨率
    geometries=True)        # 保留坐标，方便后面空间划分/画图

# ───────────────────────────────────────────────────────────
# 6. 导出 CSV（下一步喂给 ydata-profiling 做 §3/§4）
# ───────────────────────────────────────────────────────────
ee.batch.Export.table.toDrive(
    collection=table,
    description='porthills_point_table',
    fileFormat='CSV').start()

print('导出任务已提交 → GEE Tasks 里点 Run，完成后 CSV 在 Google Drive。')
print('这张表的每一行 = 一个判读点；列 = 类别 + 6波段 + 4指数 + 3地形。')
print('§3 §4 §5 全跑在它上面。')
