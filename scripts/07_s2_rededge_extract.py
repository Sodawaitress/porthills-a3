"""
US5 补充方案2 - 给211个训练点提取 Sentinel-2 红边波段(B5/B6/B7)，
测试能不能把 native_scrub vs gorse_broom 这对JM=1.46的老大难分开。
Landsat 8 没有红边波段，S2才有，所以这是L8体系里补不出来的信息。

跑法：在已经装好+认证过 earthengine-api 的那台机器上跑：
  python 07_s2_rededge_extract.py
输出：scripts/s2_rededge_by_point.csv，用真实 OID（TrainingPoints_wgs84.csv 里的
OID列，来自 TrainingPoints_raw 的 OID@，不是行号）做join key -- 之前 Sample()
join错过一次(用错了字段)，这里直接从头用真实OID，不留隐患。

⚠️ 2026-09-20更新：TrainingPoints_wgs84.csv 已经从215点(旧版，含4个后来删掉的
重复/离群点)重新导出成211点(当前canonical版本)，带真实OID列。如果你本地这份
CSV还是旧的215行版本，先 git pull 一下。
"""
import ee, os
import pandas as pd

ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))          # 相对路径，两台机都能跑
PTS_CSV = os.path.join(HERE, "TrainingPoints_wgs84.csv")
OUT_CSV = os.path.join(HERE, "s2_rededge_by_point.csv")

pts_df = pd.read_csv(PTS_CSV)
print("点数:", len(pts_df))

# 火前窗口，跟 02_check_prefire_sentinel2.py / 01_build_point_table.py 的 PRE_END 对齐
PRE_START = '2016-10-01'
PRE_END = '2017-02-12'
AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

s2 = (ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
        .filterBounds(AOI)
        .filterDate(PRE_START, PRE_END)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
n_images = s2.size().getInfo()
print("火前候选影像数:", n_images)

# 用中值合成而不是挑单景 -- 提取像元值要的是每个点都尽量拿到干净值，
# 合成比单景更能避开个别点被云盖住的情况(跟02脚本目的不同，那边是看缩略图)
composite = s2.median().select(['B5', 'B6', 'B7', 'B4', 'B8'])  # 红边x3 + Red + NIR(方便顺手算个红边NDVI)

features = []
for _, row in pts_df.iterrows():
    geom = ee.Geometry.Point([row['lon'], row['lat']])
    features.append(ee.Feature(geom, {'OID': int(row['OID'])}))
fc = ee.FeatureCollection(features)

sampled = composite.sampleRegions(collection=fc, scale=10, geometries=False)
result = sampled.getInfo()

rows = []
for f in result['features']:
    props = f['properties']
    rows.append(props)

out_df = pd.DataFrame(rows).sort_values('OID').reset_index(drop=True)
out_df = out_df.merge(pts_df[['OID', 'lon', 'lat', 'FuelClass', 'class_id', 'split']],
                       on='OID', how='left')
out_df.to_csv(OUT_CSV, index=False)
print("wrote ->", OUT_CSV)
print("匹配到红边值的点数:", len(out_df), "/", len(pts_df))

# 红边归一化植被指数 (NDVI_rededge = (B8-B5)/(B8+B5))，跟普通NDVI对比看有没有额外区分力
out_df['NDVI_re'] = (out_df['B8'] - out_df['B5']) / (out_df['B8'] + out_df['B5'])
print("\n=== gorse_broom vs native_scrub 红边波段均值对比 ===")
sub = out_df[out_df['FuelClass'].isin(['gorse_broom', 'native_scrub'])]
print(sub.groupby('FuelClass')[['B5', 'B6', 'B7', 'NDVI_re']].agg(['mean', 'std', 'count']))
