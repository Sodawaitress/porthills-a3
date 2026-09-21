"""
2017 版烧痕误判量化（对应 2024 的 22c）。2024 发现 S2 的 SCL 把深色烧痕误判成
"云影"掩掉；2017 用 Landsat 8，掩膜 QA_PIXEL `1<<4` = Cloud Shadow 同样会误杀烧痕
（01/10/11 号脚本都掩了 bit4）。这里量化：2017 火后 dNBR 采样时，掩 vs 不掩云影位，
在 290 个训练点上各能得到多少有效 dNBR、哪些类被误杀最多。

只量化、不改数据。跑法：GEE 认证过的机器。

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee, os, csv
from collections import Counter

ee.Initialize(project='genuine-hold-427410-f0')
HERE = os.path.dirname(os.path.abspath(__file__))
PTS = os.path.join(HERE, "TrainingPoints_wgs84.csv")

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
PRE_START, PRE_END = '2016-10-01', '2017-02-12'      # 同 01 号脚本
POST_START, POST_END = '2017-02-13', '2017-03-31'    # 紧火后窗(≈几景 Landsat，掩膜效应才显得出)


def scale(img):
    return img.select('SR_B.').multiply(0.0000275).add(-0.2)


def mask_full(img):      # 01/10/11 用的：掩 膨胀云1/卷云2/云3/云影4
    qa = img.select('QA_PIXEL')
    bad = (qa.bitwiseAnd(1 << 1).Or(qa.bitwiseAnd(1 << 2))
             .Or(qa.bitwiseAnd(1 << 3)).Or(qa.bitwiseAnd(1 << 4)))
    return scale(img).updateMask(bad.Not())


def mask_clouds_only(img):   # 只掩真云 1/2/3，保留云影4(=烧痕)
    qa = img.select('QA_PIXEL')
    bad = qa.bitwiseAnd(1 << 1).Or(qa.bitwiseAnd(1 << 2)).Or(qa.bitwiseAnd(1 << 3))
    return scale(img).updateMask(bad.Not())


def nbr(img):
    return img.normalizedDifference(['SR_B5', 'SR_B7'])


pts = list(csv.DictReader(open(PTS)))
cls = {int(r['OID']): r['FuelClass'] for r in pts}
fc = ee.FeatureCollection(
    [ee.Feature(ee.Geometry.Point([float(r['lon']), float(r['lat'])]), {'OID': int(r['OID'])})
     for r in pts])
n_total = len(pts)


def valid_oids(maskfn):
    coll = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(AOI)
    pre = coll.filterDate(PRE_START, PRE_END).map(maskfn).median()
    post = coll.filterDate(POST_START, POST_END).map(maskfn).median()
    dnbr = nbr(pre).subtract(nbr(post)).rename('dNBR')
    res = dnbr.sampleRegions(collection=fc, scale=30, geometries=False).getInfo()
    return {f['properties']['OID'] for f in res['features']
            if f['properties'].get('dNBR') is not None}


n_scenes = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(AOI) \
    .filterDate(POST_START, POST_END).size().getInfo()
print(f"火后窗 {POST_START}~{POST_END}: {n_scenes} 景 Landsat；训练点 {n_total}")

base = valid_oids(mask_full)          # 掩云影(现状)
relaxed = valid_oids(mask_clouds_only)  # 不掩云影(保留烧痕)
recovered = relaxed - base
print(f"\n掩云影(01/10/11 现状):   {len(base)}/{n_total} 有效 dNBR")
print(f"不掩云影(保留烧痕):      {len(relaxed)}/{n_total} 有效 dNBR")
print(f"不掩云影救回:            +{len(recovered)}")
if recovered:
    print("\n救回的点按类:")
    for c, n in sorted(Counter(cls[o] for o in recovered).items()):
        print(f"  {c:18s} +{n}")
