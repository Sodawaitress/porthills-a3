"""
2024 Port Hills fire - US2 final step: merge terrain+CHM (14, local) with
S2 spectral bands+indices (15, GEE) into one final point table, joined on FID.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import csv

out_dir = r"C:\Users\zhouy3d\Desktop\a3\2024_materials"
terrain_csv = f"{out_dir}\\TrainingPoints_2024_terrain.csv"
s2_csv = f"{out_dir}\\TrainingPoints_2024_s2.csv"
out_csv = f"{out_dir}\\PortHills2024_PointTable.csv"

with open(terrain_csv) as f:
    terrain_rows = {int(r["FID"]): r for r in csv.DictReader(f)}
with open(s2_csv) as f:
    s2_rows = {int(r["FID"]): r for r in csv.DictReader(f)}

terrain_fids = set(terrain_rows.keys())
s2_fids = set(s2_rows.keys())
print(f"terrain rows: {len(terrain_fids)}, S2 rows: {len(s2_fids)}")
print(f"in terrain but not S2: {sorted(terrain_fids - s2_fids)}")
print(f"in S2 but not terrain: {sorted(s2_fids - terrain_fids)}")

common_fids = sorted(terrain_fids & s2_fids)
terrain_fields = [f for f in list(terrain_rows.values())[0].keys() if f != "FID"]
s2_fields = [f for f in list(s2_rows.values())[0].keys() if f != "FID"]

out_fields = ["FID"] + terrain_fields + s2_fields
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()
    for fid in common_fids:
        row = {"FID": fid}
        row.update({k: terrain_rows[fid][k] for k in terrain_fields})
        row.update({k: s2_rows[fid][k] for k in s2_fields})
        w.writerow(row)

print(f"\nWrote {out_csv}: {len(common_fids)} rows x {len(out_fields)} columns")

# quick per-class count check
from collections import Counter
counts = Counter(terrain_rows[fid]["FuelClass"] for fid in common_fids)
splits = Counter((terrain_rows[fid]["FuelClass"], terrain_rows[fid]["split"]) for fid in common_fids)
print("\nPer-class counts in final point table:")
for cls in sorted(counts):
    tr = splits.get((cls, "train"), 0)
    va = splits.get((cls, "valid"), 0)
    print(f"  {cls:18s} total={counts[cls]:3d}  train={tr:3d}  valid={va:3d}")
