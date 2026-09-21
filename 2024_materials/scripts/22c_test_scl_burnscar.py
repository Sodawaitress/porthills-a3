"""
Diagnostic: is the 126/243 post-fire gap caused by SCL flagging dark BURN SCARS
as cloud shadow (class 3) and masking them out? If so it's a systematic loss of
the most-burned points, not a real cloud gap - and NOT fixable by widening the
window (22b proved widening recovers 0 points, only adds regrowth bias).

Test: same tight window as 22 (2024-02-20 -> 03-31), but the post-fire mask
drops class 3 (cloud shadow) and 11 (snow - none in Port Hills autumn), keeping
only real clouds 8/9/10. If the missing points come back, SCL-over-masking of
burn scars is confirmed as the cause.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import csv

ee.Initialize(project='genuine-hold-427410-f0')
HERE = os.path.dirname(os.path.abspath(__file__))
PTS_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_wgs84.csv")
TABLE = os.path.join(HERE, "..", "PortHills2024_PointTable.csv")

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
PRE_START, PRE_END = '2024-01-10', '2024-02-13'
POST_START, POST_END = '2024-02-20', '2024-03-31'


def mask_clouds_only(img):
    # keep class 3 (shadow) and 11 (snow); mask only real clouds + cirrus
    scl = img.select('SCL')
    mask = scl.neq(8).And(scl.neq(9)).And(scl.neq(10))
    return img.updateMask(mask).divide(10000)


def mask_full(img):  # 22's original mask, for the baseline count
    scl = img.select('SCL')
    mask = (scl.neq(3).And(scl.neq(8)).And(scl.neq(9))
            .And(scl.neq(10)).And(scl.neq(11)))
    return img.updateMask(mask).divide(10000)


def comp(start, end, cloud_pct, maskfn):
    return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(AOI).filterDate(start, end)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_pct))
            .map(maskfn).median().clip(AOI))


with open(PTS_CSV) as f:
    pts = list(csv.DictReader(f))
cls = {int(r['PID']): r['FuelClass'] for r in csv.DictReader(open(TABLE))}
fc = ee.FeatureCollection(
    [ee.Feature(ee.Geometry.Point([float(r['lon']), float(r['lat'])]),
                {'PID': int(r['PID'])}) for r in pts])


def valid_pids(maskfn):
    pre = comp(PRE_START, PRE_END, 40, maskfn)
    post = comp(POST_START, POST_END, 60, maskfn)
    dnbr = pre.normalizedDifference(['B8', 'B12']).subtract(
        post.normalizedDifference(['B8', 'B12'])).multiply(1000).rename('dNBR')
    res = dnbr.sampleRegions(collection=fc, scale=10, geometries=False).getInfo()
    return {f['properties']['PID'] for f in res['features']
            if f['properties'].get('dNBR') is not None}


base = valid_pids(mask_full)          # = 22, masks shadow too
relaxed = valid_pids(mask_clouds_only)  # keeps shadow (= burn scars)
print(f"22 original mask (masks shadow):  {len(base)}/{len(pts)} valid")
print(f"clouds-only mask (keeps shadow):  {len(relaxed)}/{len(pts)} valid")
print(f"recovered by not masking shadow:  +{len(relaxed - base)}\n")

from collections import Counter
rec = Counter(cls[p] for p in (relaxed - base))
print("recovered points by class:")
for c in sorted(rec):
    print(f"  {c:18s} +{rec[c]}")
