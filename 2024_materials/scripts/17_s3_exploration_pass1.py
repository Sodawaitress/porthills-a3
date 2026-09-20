"""
2024 Port Hills fire - S3 First pass (US3-equivalent), same method as 2017's
03_data_exploration_pass1.py: nulls / constant columns / duplicate rows / IQR
outlier fences, boxplots by class.

Columns: this time includes ALL 10 S2 bands (not just 6 like Landsat) + 5
indices (NDVI/NBR/NDWI/NDRE/BSI, NDRE is new) + elev/slope/northness/chm
(CHM is new - 2017 only had 3 terrain vars, no structural height).

Author: Claude (for Yu Zhou), 2026-09-21
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\exploration"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV)
print("Total rows:", len(df))

COLS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
        "NDVI", "NBR", "NDWI", "NDRE", "BSI",
        "elev", "slope", "northness", "chm"]

print("\n=== Nulls ===")
nulls = df[COLS].isna().sum()
print(nulls[nulls > 0] if nulls.sum() > 0 else "none")

print("\n=== Constant columns (no predictive power) ===")
for c in df.columns:
    if df[c].nunique() == 1:
        print(f"  {c}: constant, always {df[c].iloc[0]} -> should drop")

print("\n=== Duplicate rows ===")
dup = df.duplicated(subset=COLS).sum()
print(f"duplicate rows: {dup}")

print("\n=== First pass outliers: IQR fences ===")
outlier_summary = []
for c in COLS:
    q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (df[c] < lo) | (df[c] > hi)
    n_out = mask.sum()
    outlier_summary.append((c, n_out, lo, hi))
    print(f"  {c:10s}: {n_out:3d} outliers (lo={lo:.4f} hi={hi:.4f})")

outlier_summary.sort(key=lambda r: -r[1])
print("\nby severity:", [(r[0], r[1]) for r in outlier_summary])

fig, axes = plt.subplots(4, 5, figsize=(22, 16))
for ax, c in zip(axes.flat, COLS):
    df.boxplot(column=c, by="FuelClass", ax=ax, rot=45)
    ax.set_title(c, fontsize=10)
    ax.set_xlabel("")
for ax in axes.flat[len(COLS):]:
    ax.axis("off")
plt.suptitle("")
plt.tight_layout()
out_png = os.path.join(OUT_DIR, "boxplots_by_class_2024.png")
plt.savefig(out_png, dpi=120)
print("\nBoxplots ->", out_png)
