"""
2024 Port Hills fire - S3 Second Pass (US3-equivalent), same method + thresholds
as 2017's 03d_normality_by_class.py: skew/kurtosis PER CLASS (not pooled -
2017 found pooling hides multi-modality that per-class reveals), flagged
non-normal if |skew|>1 or |kurt|>2.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import pandas as pd
import collections
from scipy import stats

CSV = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv"
df = pd.read_csv(CSV)

COLS = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12",
        "NDVI", "NBR", "NDWI", "NDRE", "BSI",
        "elev", "slope", "northness", "chm"]

flags = []
for cls, g in df.groupby("FuelClass"):
    n = len(g)
    for c in COLS:
        sk = stats.skew(g[c])
        ku = stats.kurtosis(g[c])
        non_normal = abs(sk) > 1 or abs(ku) > 2
        if non_normal:
            flags.append((cls, c, n, sk, ku))

print(f"{'class':18s} {'var':10s} {'n':>4s} {'skew':>8s} {'kurt':>8s}")
for cls, c, n, sk, ku in flags:
    print(f"{cls:18s} {c:10s} {n:4d} {sk:8.3f} {ku:8.3f}")

total_combos = df["FuelClass"].nunique() * len(COLS)
print(f"\n{len(flags)} / {total_combos} (class, var) combos non-normal")

by_class = collections.Counter(f[0] for f in flags)
by_var = collections.Counter(f[1] for f in flags)
print("by class:", dict(by_class))
print("by var:  ", dict(by_var))

print("\nclass sample sizes:")
print(df.groupby("FuelClass").size())

# worst offenders (biggest |skew| or |kurt|)
flags_sorted = sorted(flags, key=lambda f: max(abs(f[3]), abs(f[4])), reverse=True)
print("\nworst 5 (class, var) combos:")
for cls, c, n, sk, ku in flags_sorted[:5]:
    print(f"  {cls:18s} {c:10s} skew={sk:.3f} kurt={ku:.3f}")
