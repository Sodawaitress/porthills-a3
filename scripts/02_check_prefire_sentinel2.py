"""
US1.6 辅助 - 拉 2017 年火前最后一段时间的 Sentinel-2 真彩色图，
核对几个可疑训练点（2015 航片太老，跟不上火前最后状态）。

跑法：跟 01_build_point_table.py 一样，GEE Python（Colab 里
`import ee; ee.Authenticate()` 一次即可）。

★ 只需要改 SUSPECT_POINTS（想核对哪几个点就填哪几个）。
"""
import ee
ee.Initialize(project='genuine-hold-427410-f0')  # 新版 ee 必须给 project

# ───────────────────────────────────────────────────────────
# 0. 要核对的可疑点（从 ArcGIS Pro 目视抽查里挑出来的）
# ───────────────────────────────────────────────────────────
SUSPECT_POINTS = {
    "pasture-building": (172.615151, -43.596901),   # 疑似压在建筑物上
    "gorse-building":   (172.603357, -43.628854),   # 疑似压在建筑物上
    "pasture-yellow":   (172.620589, -43.619510),   # 疑似开花金雀花混进牧草地
}

# ───────────────────────────────────────────────────────────
# 1. 火前最后一段窗口：跟 01_build_point_table.py 的 PRE_END 对齐
#    （2017-02-13 起火，往前抓够长一段避云，S2 2015年中才有数据，
#     窗口拉宽到 2016-10 起，跟 Landsat 那份窗口一致，方便对照）
# ───────────────────────────────────────────────────────────
PRE_START = '2016-10-01'
PRE_END   = '2017-02-12'

# ⚠️ 必须先按位置筛(filterBounds)，否则会从全球挑图、选中的根本不在 Port Hills
AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
# ⚠️ 用 L1C TOA(S2_HARMONIZED)不用 L2A/SR：Port Hills 火前 S2 地表反射率不存在
#    (SR 这片 2017-03 才有)。目视核对点位用 TOA 真彩色足够。
s2 = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
        .filterBounds(AOI)
        .filterDate(PRE_START, PRE_END)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

print('候选影像数:', s2.size().getInfo())

# 按云量排序，取最干净的一张做底图（也可以改成 .median() 做合成，
# 但合成会糊掉细节，核对具体地物用单景最干净的更直观）
best = s2.sort('CLOUDY_PIXEL_PERCENTAGE').first()
date = ee.Date(best.get('system:time_start')).format('YYYY-MM-dd').getInfo()
cloud = best.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
print(f'选中影像日期: {date}, 云量: {cloud:.1f}%')

rgb = best.select(['B4', 'B3', 'B2'])  # 真彩色
vis = {'min': 0, 'max': 2500}

# ───────────────────────────────────────────────────────────
# 2. 给每个可疑点裁一小块、生成缩略图链接（浏览器直接打开看）
# ───────────────────────────────────────────────────────────
HALF_DEG = 0.003  # 约300m见方，够看清点位周边

for name, (lon, lat) in SUSPECT_POINTS.items():
    region = ee.Geometry.Rectangle([lon - HALF_DEG, lat - HALF_DEG,
                                     lon + HALF_DEG, lat + HALF_DEG])
    url = rgb.getThumbURL({
        'region': region,
        'dimensions': 512,
        'min': vis['min'], 'max': vis['max'],
        'format': 'png',
    })
    print(f'{name}: {url}')

print()
print(f'以上是 {date}（火前最后一批干净影像，云量{cloud:.1f}%）的真彩色缩略图链接。')
print('浏览器打开对比 2015 航片，看这三个点火前最后状态是不是还跟标签一致。')
