"""
US5 补充方案1 - 给211个训练点提取"金雀花花期(春季)"的光谱值，
测试能不能把 native_scrub vs gorse_broom 分开。
文献依据: gorse开花期(NZ的8-10月)大片鲜黄色，用春季影像能把它从其他灌丛类型
里分出来 (Satellite mapping of gorse at regional scales,
https://www.researchgate.net/publication/230694091)。

跟火本身的时间点无关 -- gorse开不开花是植物物候特性，不是2017年那次火决定的，
所以随便挑哪几年的春季影像都行，只要不是火后年份重新长出来的植被(参考CHM那次
讨论过的同一个逻辑：pre-fire或at least独立于本次火的都可以)。用多年中值合成
是为了避开"单张影像刚好被云挡住"这个文献里提到的已知限制。

跑法：在已装好+认证过 earthengine-api 的机器上跑。
输出：scripts/gorse_flowering_by_point.csv，用真实OID(TrainingPoints_wgs84.csv
里的OID列)做join key，不用行号。

⚠️ 2026-09-20更新：TrainingPoints_wgs84.csv 已经从215点(旧版，含4个后来删掉的
重复/离群点)重新导出成211点(当前canonical版本)，带真实OID列。如果你本地这份
CSV还是旧的215行版本，先 git pull 一下。
"""
import ee, os
import pandas as pd

ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))          # 相对路径，两台机都能跑
PTS_CSV = os.path.join(HERE, "TrainingPoints_wgs84.csv")
OUT_CSV = os.path.join(HERE, "gorse_flowering_by_point.csv")

pts_df = pd.read_csv(PTS_CSV)
print("点数:", len(pts_df))

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

# 火前3个春季(8月15日-10月15日)，跟主特征栈一样用Landsat 8保持波段/分辨率一致，
# 用多年中值合成避开云 -- 都在2017年2月的火之前，不存在CHM那次的"火后重新长"问题
SPRING_WINDOWS = [('2014-08-15', '2014-10-15'),
                   ('2015-08-15', '2015-10-15'),
                   ('2016-08-15', '2016-10-15')]

l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(AOI)
spring_imgs = ee.ImageCollection([])
for start, end in SPRING_WINDOWS:
    coll = l8.filterDate(start, end).filter(ee.Filter.lt('CLOUD_COVER', 30))
    spring_imgs = spring_imgs.merge(coll)

n_images = spring_imgs.size().getInfo()
print("春季候选影像数(3年8-10月合计):", n_images)

def scale_bands(img):
    optical = img.select('SR_B.').multiply(0.0000275).add(-0.2)
    return img.addBands(optical, None, True)

spring_scaled = spring_imgs.map(scale_bands)
composite = spring_scaled.median().select(
    ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])  # Blue/Green/Red/NIR/SWIR1/SWIR2

features = []
for _, row in pts_df.iterrows():
    geom = ee.Geometry.Point([row['lon'], row['lat']])
    features.append(ee.Feature(geom, {'OID': int(row['OID'])}))
fc = ee.FeatureCollection(features)

sampled = composite.sampleRegions(collection=fc, scale=30, geometries=False)
result = sampled.getInfo()

rows = [f['properties'] for f in result['features']]
out_df = pd.DataFrame(rows).sort_values('OID').reset_index(drop=True)
out_df = out_df.merge(pts_df[['OID', 'lon', 'lat', 'FuelClass', 'class_id', 'split']],
                       on='OID', how='left')

# 花期"黄度"指标: 黄色反射红+绿高、蓝低 -> 用 (Red+Green)/2 - Blue 做一个简单黄度指数
out_df['yellow_index'] = (out_df['SR_B4'] + out_df['SR_B3']) / 2 - out_df['SR_B2']
out_df['NDVI_spring'] = (out_df['SR_B5'] - out_df['SR_B4']) / (out_df['SR_B5'] + out_df['SR_B4'])

out_df.to_csv(OUT_CSV, index=False)
print("wrote ->", OUT_CSV)
print("匹配到春季波段值的点数:", len(out_df), "/", len(pts_df))

print("\n=== gorse_broom vs native_scrub 花期波段/黄度指数对比 ===")
sub = out_df[out_df["FuelClass"].isin(["gorse_broom", "native_scrub"])]
print(sub.groupby("FuelClass")[["SR_B2", "SR_B3", "SR_B4", "yellow_index", "NDVI_spring"]]
      .agg(["mean", "std", "count"]))
