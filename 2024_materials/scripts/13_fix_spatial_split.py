"""
Fix the gorse_broom 45/5 train/valid imbalance from 12_place_training_points.py.
Cause: 300m blocks assigned to train/valid by a single global random draw -
fine on average, but with only 69 blocks and gorse_broom concentrated in a
handful of them, one unlucky draw starved its valid set.

Fix: keep the same block-based logic (still no point-level random splitting -
that's still the leakage risk we're avoiding), but choose the block->split
assignment to balance EVERY class's train fraction near 70%, not just the
overall block count. Try many random starting shuffles, greedily assign each
block to whichever side keeps the per-class fractions closer to 0.7, and keep
the best of many attempts.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy
import numpy as np

arcpy.env.overwriteOutput = True
out_dir = r"C:\Users\zhouy3d\Desktop\a3\2024_materials"
pts_fc = f"{out_dir}\\TrainingPoints_2024_raw.shp"

# ---- load points: block_id (already computed by script 12) + class ----
classes = []
block_ids = []
with arcpy.da.SearchCursor(pts_fc, ["FuelClass", "block_id"]) as cur:
    for cls, bid in cur:
        classes.append(cls)
        block_ids.append(bid)
classes = np.array(classes)
block_ids = np.array(block_ids)
class_list = sorted(set(classes))
unique_blocks = sorted(set(block_ids.tolist()))

# block x class point-count matrix
block_class_count = {b: {c: 0 for c in class_list} for b in unique_blocks}
for c, b in zip(classes, block_ids):
    block_class_count[b][c] += 1

class_totals = {c: int(np.sum(classes == c)) for c in class_list}
TARGET = 0.70


def try_assignment(seed):
    rng = np.random.default_rng(seed)
    order = unique_blocks.copy()
    rng.shuffle(order)
    train_count = {c: 0 for c in class_list}
    assignment = {}
    for b in order:
        counts = block_class_count[b]
        # score each option: sum of squared deviation from target across classes
        def score(is_train):
            s = 0.0
            for c in class_list:
                total = class_totals[c]
                if total == 0:
                    continue
                tc = train_count[c] + (counts[c] if is_train else 0)
                frac = tc / total if total else 0
                # only "counts" toward this class if the class has points in it,
                # but we must project final fraction assuming untouched blocks go 70/30 on average -
                # simplify: just balance based on assigned-so-far + this block
                s += (frac - TARGET) ** 2 * total  # weight by class size so big classes dominate less noisily
            return s
        s_train = score(True)
        s_valid = score(False)
        put_train = s_train <= s_valid
        assignment[b] = "train" if put_train else "valid"
        if put_train:
            for c in class_list:
                train_count[c] += counts[c]
    return assignment, train_count


best = None
best_penalty = None
for seed in range(500):
    assignment, train_count = try_assignment(seed)
    max_dev = max(abs(train_count[c] / class_totals[c] - TARGET) for c in class_list)
    min_valid = min(class_totals[c] - train_count[c] for c in class_list)
    # penalize: worst per-class deviation from 70%, and reject if any class's valid < 10
    penalty = max_dev + (0 if min_valid >= 10 else 10)
    if best_penalty is None or penalty < best_penalty:
        best_penalty = penalty
        best = (seed, assignment, train_count, min_valid, max_dev)

seed, assignment, train_count, min_valid, max_dev = best
print(f"Best seed: {seed}, max per-class deviation from 70%: {max_dev:.3f}, min valid count: {min_valid}")
print("\nPer-class train/valid after rebalancing:")
for c in class_list:
    tr = train_count[c]
    va = class_totals[c] - tr
    print(f"  {c:18s} train={tr:3d}  valid={va:3d}  total={class_totals[c]:3d}  train_frac={tr/class_totals[c]:.2f}")

# ---- write back to the shapefile + csv ----
new_splits = [assignment[b] for b in block_ids]
with arcpy.da.UpdateCursor(pts_fc, ["block_id", "split"]) as cur:
    for row in cur:
        row[1] = assignment[row[0]]
        cur.updateRow(row)

wgs84 = arcpy.SpatialReference(4326)
pts_wgs84 = "in_memory/pts_wgs84_v2"
arcpy.management.Project(pts_fc, pts_wgs84, wgs84)
csv_path = f"{out_dir}\\TrainingPoints_2024_wgs84.csv"
with open(csv_path, "w") as f:
    f.write("lon,lat,FuelClass,class_id,split,block_id\n")
    with arcpy.da.SearchCursor(pts_wgs84, ["SHAPE@XY", "FuelClass", "class_id", "split", "block_id"]) as cur:
        for (x, y), cls, cid, split, bid in cur:
            f.write(f"{x:.6f},{y:.6f},{cls},{cid},{split},{bid}\n")
print(f"\nUpdated {pts_fc} and re-wrote {csv_path}")
