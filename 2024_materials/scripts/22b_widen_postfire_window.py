"""
2024 Port Hills fire - B decision (widen the post-fire window to recover the
126/243 points that fell in cloud gaps with the tight window 22 used).

WHY a separate script, not an edit to 22: 22's window (2024-02-20 -> 03-31)
is deliberately identical to the severity map (02_dNBR JS) this project treats
as refugia ground truth. Keep 22 as that consistent baseline. This script
EXPLORES wider windows and, crucially, MEASURES the vegetation-recovery bias
each widening buys - the 2017 project found a 2-month-later post date carried
a 22-78% systematic dNBR bias (workflow.md, "postfire alt dates" record), so
widening is not free. Turning that limitation into a number is the point.

Method: same pre window + same NBR formula + same x1000 scaling as 22, only
POST_END moves later. Bias = for points valid in BOTH the tight baseline and a
widened window, how much did dNBR shift.

Run on the GEE-authenticated machine: python 22b_widen_postfire_window.py

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import csv
from statistics import median

ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))
PTS_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_wgs84.csv")
OUT_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_dnbr_widened.csv")

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
PRE_START, PRE_END = '2024-01-10', '2024-02-13'   # same as 22
POST_START = '2024-02-20'                          # same as 22
# tight baseline end (= 22, = severity map) then two progressively wider ends
POST_ENDS = ['2024-03-31', '2024-04-30', '2024-05-31']


def mask_s2(img):
    scl = img.select('SCL')
    mask = (scl.neq(3).And(scl.neq(8)).And(scl.neq(9))
            .And(scl.neq(10)).And(scl.neq(11)))
    return img.updateMask(mask).divide(10000)


def get_composite(start, end, cloud_pct):
    return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(AOI).filterDate(start, end)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_pct))
            .map(mask_s2).median().clip(AOI))


pre_img = get_composite(PRE_START, PRE_END, 40)
pre_nbr = pre_img.normalizedDifference(['B8', 'B12']).rename('NBR_pre')

with open(PTS_CSV) as f:
    pts_rows = list(csv.DictReader(f))
features = [ee.Feature(ee.Geometry.Point([float(r['lon']), float(r['lat'])]),
                       {'PID': int(r['PID'])}) for r in pts_rows]
fc = ee.FeatureCollection(features)
n_total = len(pts_rows)


def dnbr_at_points(post_end):
    post_img = get_composite(POST_START, post_end, 60)
    post_nbr = post_img.normalizedDifference(['B8', 'B12']).rename('NBR_post')
    dnbr = pre_nbr.subtract(post_nbr).multiply(1000).rename('dNBR')
    sampled = dnbr.sampleRegions(collection=fc, scale=10, geometries=False)
    res = sampled.getInfo()
    return {f['properties']['PID']: f['properties'].get('dNBR')
            for f in res['features']
            if f['properties'].get('dNBR') is not None}


# tight baseline first, then compare each wider window against it
per_window = {end: dnbr_at_points(end) for end in POST_ENDS}
baseline = per_window[POST_ENDS[0]]

print(f"Post window START fixed at {POST_START}. Points total = {n_total}.\n")
print(f"{'POST_END':12s} {'valid':>6s} {'recovered':>10s}  "
      f"{'median dNBR shift vs tight':>26s}  {'median |shift|':>13s}")
for end in POST_ENDS:
    vals = per_window[end]
    overlap = [pid for pid in vals if pid in baseline]
    shifts = [vals[pid] - baseline[pid] for pid in overlap]
    recov = len(vals) - len(baseline)
    med_shift = f"{median(shifts):+.1f}" if shifts else "-"
    med_abs = f"{median(abs(s) for s in shifts):.1f}" if shifts else "-"
    tag = "  (= 22, baseline)" if end == POST_ENDS[0] else ""
    print(f"{end:12s} {len(vals):6d} {recov:+10d}  {med_shift:>26s}  {med_abs:>13s}{tag}")

# write the widest window's values so the merge step has the fullest coverage;
# the report still has to justify the window choice using the bias table above
widest = per_window[POST_ENDS[-1]]
with open(OUT_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['PID', 'dNBR', 'post_end_used'])
    w.writeheader()
    for pid in sorted(widest):
        w.writerow({'PID': pid, 'dNBR': widest[pid], 'post_end_used': POST_ENDS[-1]})
print(f"\nWrote {OUT_CSV} ({len(widest)}/{n_total} valid, window {POST_START}->{POST_ENDS[-1]})")
print("^ widest window written for max coverage; pick final window in the report "
      "using the bias table (recovered points vs dNBR shift).")
