"""
2024 Port Hills fire - place training/validation points (US1.5-equivalent).

Correction from chat: I told Yu "15m spacing = half a Sentinel-2 pixel" -
that's wrong, half of 10m is 5m not 15m. 2017's 30m spacing rule was actually
a FULL Landsat pixel (not half), to keep two points from landing in the same
pixel. The half-pixel-radius rule (15m for 2017) was a SEPARATE thing - the
purity-check buffer, not point spacing. Correct S2 analogues:
  point spacing (CreateRandomPoints minimum distance) = 10m (1 full S2 pixel)
  purity-check buffer radius (separate QA step, not run here yet)   = 5m

50 points/class target (same as 2017's per-class target), min spacing 10m.
Then 300m spatial-block 70/30 split, same method as 2017 (per-point random
splitting of points this close together causes spatial-autocorrelation
leakage - see workflow.md's US1.5 method record + the Ploton/Karasiak refs
already in references.md).

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy
import numpy as np

arcpy.env.overwriteOutput = True
nztm = arcpy.SpatialReference(2193)
wgs84 = arcpy.SpatialReference(4326)

out_dir = r"C:\Users\zhouy3d\Desktop\a3\2024_materials"
CLASSES = {
    "pasture":         1,
    "gorse_broom":     2,
    "exotic_pine":     3,
    "broadleaf_scrub": 4,
    "cleared_pine":    5,
}
N_PER_CLASS = 50
MIN_DIST = "10 Meters"

all_points_fc = f"{out_dir}\\TrainingPoints_2024_raw.shp"
arcpy.management.CreateFeatureclass(out_dir, "TrainingPoints_2024_raw.shp", "POINT", spatial_reference=nztm)
arcpy.management.AddField(all_points_fc, "FuelClass", "TEXT", field_length=20)
arcpy.management.AddField(all_points_fc, "class_id", "SHORT")

with arcpy.da.InsertCursor(all_points_fc, ["SHAPE@", "FuelClass", "class_id"]) as ins:
    for cls, cid in CLASSES.items():
        src_fc = f"{out_dir}\\{cls}_2024.shp"
        n_features = int(arcpy.management.GetCount(src_fc)[0])
        if n_features > 1:
            # guard against the 2017 CreateRandomPoints bug (N points PER polygon,
            # not per class) - dissolve first if this ever isn't already one feature
            dissolved = f"in_memory/{cls}_dissolved"
            arcpy.management.Dissolve(src_fc, dissolved)
            src_fc = dissolved

        tmp_pts = f"in_memory/{cls}_pts"
        arcpy.management.CreateRandomPoints(
            out_path="in_memory", out_name=f"{cls}_pts",
            constraining_feature_class=src_fc,
            number_of_points_or_field=N_PER_CLASS,
            minimum_allowed_distance=MIN_DIST)
        n_made = int(arcpy.management.GetCount(tmp_pts)[0])
        print(f"{cls:18s} requested {N_PER_CLASS}, got {n_made}")
        with arcpy.da.SearchCursor(tmp_pts, ["SHAPE@"]) as cur:
            for (shp,) in cur:
                ins.insertRow([shp, cls, cid])

total = int(arcpy.management.GetCount(all_points_fc)[0])
print(f"\nTotal points placed: {total}")

# ---- 300m spatial-block 70/30 split (same method as 2017) ----
desc = arcpy.Describe(all_points_fc)
ext = desc.extent
block = 300.0
coords = []
with arcpy.da.SearchCursor(all_points_fc, ["SHAPE@XY"]) as cur:
    for (xy,) in cur:
        coords.append(xy)
coords = np.array(coords)
bx = np.floor((coords[:, 0] - ext.XMin) / block).astype(int)
by = np.floor((coords[:, 1] - ext.YMin) / block).astype(int)
block_id = bx * 100000 + by   # unique per (bx,by) cell

rng = np.random.default_rng(42)
unique_blocks = np.unique(block_id)
rng.shuffle(unique_blocks)
n_train_blocks = int(round(0.7 * len(unique_blocks)))
train_blocks = set(unique_blocks[:n_train_blocks].tolist())

arcpy.management.AddField(all_points_fc, "split", "TEXT", field_length=10)
arcpy.management.AddField(all_points_fc, "block_id", "LONG")
with arcpy.da.UpdateCursor(all_points_fc, ["OID@", "split", "block_id"]) as cur:
    for i, row in enumerate(cur):
        row[1] = "train" if block_id[i] in train_blocks else "valid"
        row[2] = int(block_id[i])
        cur.updateRow(row)

print(f"\nSpatial blocks: {len(unique_blocks)} total, {len(train_blocks)} -> train")
print("\nPer-class train/valid counts:")
counts = {}
with arcpy.da.SearchCursor(all_points_fc, ["FuelClass", "split"]) as cur:
    for cls, split in cur:
        counts.setdefault(cls, {"train": 0, "valid": 0})[split] += 1
for cls in CLASSES:
    c = counts.get(cls, {"train": 0, "valid": 0})
    print(f"  {cls:18s} train={c['train']:3d}  valid={c['valid']:3d}  total={c['train']+c['valid']:3d}")

# ---- also export WGS84 lon/lat CSV, for GEE sampling later (US2-equivalent) ----
pts_wgs84 = "in_memory/pts_wgs84"
arcpy.management.Project(all_points_fc, pts_wgs84, wgs84)
csv_path = f"{out_dir}\\TrainingPoints_2024_wgs84.csv"
with open(csv_path, "w") as f:
    f.write("lon,lat,FuelClass,class_id,split,block_id\n")
    with arcpy.da.SearchCursor(pts_wgs84, ["SHAPE@XY", "FuelClass", "class_id", "split", "block_id"]) as cur:
        for (x, y), cls, cid, split, bid in cur:
            f.write(f"{x:.6f},{y:.6f},{cls},{cid},{split},{bid}\n")
print(f"\nWrote {csv_path}")
