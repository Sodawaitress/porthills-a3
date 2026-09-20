"""
2024 Port Hills fire - US2 equivalent: sample the Sentinel-2 pre-fire feature
stack (bands + spectral indices) at the 250 training points.

Run on a GEE-authenticated machine: python 15_sample_s2_features.py
Reads 2024_materials/TrainingPoints_2024_wgs84.csv (relative path, same trick
2017's 07_s2_rededge_extract.py used - works on either machine after git pull,
no path edits needed). Terrain/CHM were already sampled locally (14, no GEE
needed for those) -> 16 merges both into the final point table.

Why Sentinel-2 as the PRIMARY stack this time (not just a red-edge add-on like
2017): for the 2017 fire, S2 SR wasn't yet operational pre-fire, so Landsat 8
was the only option. For 2024, full S2 coverage exists, giving 10m native
resolution (vs 30m) and native red-edge bands (2017 could only bolt red-edge
on as an afterthought via a separate sampling pass, 07/08).

Indices, same formulas/citations as 2017's stack (references.md C group),
translated to S2 band numbers:
  NDVI = (B8-B4)/(B8+B4)             Rouse 1974
  NBR  = (B8-B12)/(B8+B12)           Key & Benson 2006 (matches 01b's dNBR NBR)
  NDWI = (B3-B8)/(B3+B8)             McFeeters 1996
  BSI  = ((B11+B4)-(B8+B2))/((B11+B4)+(B8+B2))
  NDRE = (B8-B5)/(B8+B5)             Barnes et al. 2000, S2-only (2017 had to
                                      bolt this on separately in 07/08 - now
                                      it's just part of the main stack)

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import csv

ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))
PTS_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_wgs84.csv")
OUT_CSV = os.path.join(HERE, "..", "TrainingPoints_2024_s2.csv")

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
PRE_START, PRE_END = '2024-01-10', '2024-02-13'   # same window as 01b/02's dNBR pre-fire composite


def mask_s2(img):
    scl = img.select('SCL')
    mask = (scl.neq(3).And(scl.neq(8)).And(scl.neq(9))
            .And(scl.neq(10)).And(scl.neq(11)))
    return img.updateMask(mask).divide(10000)


s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
      .filterBounds(AOI).filterDate(PRE_START, PRE_END)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
      .map(mask_s2))
n_images = s2.size().getInfo()
print("Pre-fire S2 scene count:", n_images)

pre = s2.median().clip(AOI)

ndvi = pre.normalizedDifference(['B8', 'B4']).rename('NDVI')
nbr = pre.normalizedDifference(['B8', 'B12']).rename('NBR')
ndwi = pre.normalizedDifference(['B3', 'B8']).rename('NDWI')
ndre = pre.normalizedDifference(['B8', 'B5']).rename('NDRE')
bsi = pre.expression(
    '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))',
    {'SWIR': pre.select('B11'), 'RED': pre.select('B4'),
     'NIR': pre.select('B8'), 'BLUE': pre.select('B2')}).rename('BSI')

bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
stack = pre.select(bands).addBands([ndvi, nbr, ndwi, ndre, bsi])

with open(PTS_CSV) as f:
    reader = csv.DictReader(f)
    pts_rows = list(reader)
print("Points to sample:", len(pts_rows))

features = []
for row in pts_rows:
    geom = ee.Geometry.Point([float(row['lon']), float(row['lat'])])
    features.append(ee.Feature(geom, {'FID': int(row['FID'])}))
fc = ee.FeatureCollection(features)

sampled = stack.sampleRegions(collection=fc, scale=10, geometries=False)
result = sampled.getInfo()

out_rows = {f['properties']['FID']: f['properties'] for f in result['features']}
n_missing = sum(1 for row in pts_rows if int(row['FID']) not in out_rows)
print(f"Points with no S2 value returned (masked/cloud gap): {n_missing} / {len(pts_rows)}")

fieldnames = ['FID'] + bands + ['NDVI', 'NBR', 'NDWI', 'NDRE', 'BSI']
with open(OUT_CSV, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for fid in sorted(out_rows.keys()):
        props = out_rows[fid]
        w.writerow({k: props.get(k) for k in fieldnames})
print(f"Wrote {OUT_CSV}")
