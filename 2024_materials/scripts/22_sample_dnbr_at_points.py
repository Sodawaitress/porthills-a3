"""
2024 Port Hills fire - US4-equivalent prep: sample post-fire S2 + compute dNBR
at the 243 training points, same pre/post windows and NBR formula already
used for the severity map (01b/02_dNBR_2024_clip_and_refugia.js), same x1000
USGS scaling 2017's point table used (its RMSE~231 in 04_regression_dnbr.py
only makes sense on that scale).

Run on the GEE-authenticated machine: python 22_sample_dnbr_at_points.py

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import csv

ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))
PTS_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_wgs84.csv")
OUT_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_dnbr.csv")

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
# same windows as 02_dNBR_2024_clip_and_refugia.js (the severity map this
# project already treats as ground truth for refugia) - keep dNBR at the
# points consistent with the dNBR raster already produced
# pre window widened to 2023-12-01 to match 15 (still pre-fire summer, veg stable;
# the tight 2024-01-10 window only had 2 scenes -> 65 pts fell in pre-fire cloud
# holes even with the full mask). Post window unchanged (= severity map).
PRE_START, PRE_END = '2023-12-01', '2024-02-13'
POST_START, POST_END = '2024-02-20', '2024-03-31'


def mask_full(img):
    # pre-fire: no burn scars yet, so mask cloud shadow (3) + snow (11) too
    scl = img.select('SCL')
    mask = (scl.neq(3).And(scl.neq(8)).And(scl.neq(9))
            .And(scl.neq(10)).And(scl.neq(11)))
    return img.updateMask(mask).divide(10000)


def mask_clouds_only(img):
    # post-fire: SCL flags dark BURN SCARS as cloud shadow (class 3) and masks
    # them, so the tight-window mask dropped 126/243 points - the MOST burned
    # ones (pasture 12/47 etc). Widening the window recovered 0 (22b: only added
    # -142 regrowth bias). Root cause proven in 22c: keeping class 3 recovers +65
    # points (117->182), no time bias. So post-fire we mask only real clouds
    # 8/9/10 and KEEP shadow (= burn scars). Occasional true shadow that slips
    # through is diluted by the multi-scene median. See workflow.md method record.
    scl = img.select('SCL')
    mask = scl.neq(8).And(scl.neq(9)).And(scl.neq(10))
    return img.updateMask(mask).divide(10000)


def get_composite(start, end, cloud_pct, maskfn):
    return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(AOI).filterDate(start, end)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_pct))
            .map(maskfn).median().clip(AOI))


pre_img = get_composite(PRE_START, PRE_END, 40, mask_full)
post_img = get_composite(POST_START, POST_END, 60, mask_clouds_only)

pre_nbr = pre_img.normalizedDifference(['B8', 'B12']).rename('NBR_pre')
post_nbr = post_img.normalizedDifference(['B8', 'B12']).rename('NBR_post')
dnbr = pre_nbr.subtract(post_nbr).multiply(1000).rename('dNBR')

stack = post_img.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']).rename(
    ['post_B2', 'post_B3', 'post_B4', 'post_B8', 'post_B11', 'post_B12']
).addBands([pre_nbr, post_nbr, dnbr])

with open(PTS_CSV) as f:
    pts_rows = list(csv.DictReader(f))
print("Points to sample:", len(pts_rows))

features = [ee.Feature(ee.Geometry.Point([float(r['lon']), float(r['lat'])]),
                        {'PID': int(r['PID'])}) for r in pts_rows]
fc = ee.FeatureCollection(features)

sampled = stack.sampleRegions(collection=fc, scale=10, geometries=False)
result = sampled.getInfo()
out_rows = {f['properties']['PID']: f['properties'] for f in result['features']}
n_missing = sum(1 for r in pts_rows if int(r['PID']) not in out_rows
                 or out_rows[int(r['PID'])].get('dNBR') is None)
print(f"Points with no post-fire value (cloud gap): {n_missing} / {len(pts_rows)}")

fieldnames = ['PID', 'post_B2', 'post_B3', 'post_B4', 'post_B8', 'post_B11', 'post_B12',
              'NBR_pre', 'NBR_post', 'dNBR']
with open(OUT_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for pid in sorted(out_rows.keys()):
        w.writerow({k: out_rows[pid].get(k) for k in fieldnames})
print(f"Wrote {OUT_CSV}")
