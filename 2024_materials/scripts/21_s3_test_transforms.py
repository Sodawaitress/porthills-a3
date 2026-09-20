"""
2024 Port Hills fire - S3 transform testing, same method as 2017's
03f_test_transforms.py: test log/sqrt/z-score on the worst normality
offenders found in 19's per-class skew/kurt check.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import pandas as pd
import numpy as np
from scipy import stats

CSV = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv"
df = pd.read_csv(CSV)

# worst offenders from 19_s3_normality_by_class.py - chm is non-normal in ALL
# 5 classes (right-skewed, structural: mostly-near-0 + a long tail of real
# canopy), plus the next worst non-chm ones (pasture/elev, exotic_pine/northness)
targets = [
    ("cleared_pine", "chm"),
    ("broadleaf_scrub", "chm"),
    ("gorse_broom", "chm"),
    ("exotic_pine", "chm"),
    ("pasture", "chm"),
    ("pasture", "elev"),
    ("exotic_pine", "northness"),
]


def skew_kurt(x):
    return stats.skew(x), stats.kurtosis(x)


print(f"{'class':18s} {'var':10s} {'transform':10s} {'skew':>8s} {'kurt':>8s}")
for cls, var in targets:
    x = df.loc[df["FuelClass"] == cls, var].values
    sk0, ku0 = skew_kurt(x)
    print(f"{cls:18s} {var:10s} {'raw':10s} {sk0:8.3f} {ku0:8.3f}")

    if (x > 0).all():
        sk, ku = skew_kurt(np.log(x))
        print(f"{'':18s} {'':10s} {'log':10s} {sk:8.3f} {ku:8.3f}")
        sk, ku = skew_kurt(np.sqrt(x))
        print(f"{'':18s} {'':10s} {'sqrt':10s} {sk:8.3f} {ku:8.3f}")
    elif (x >= 0).all():
        # chm has true zeros (no canopy) - log undefined, but log1p works and
        # is the standard fix for "mostly zero, some positive" distributions
        sk, ku = skew_kurt(np.log1p(x))
        print(f"{'':18s} {'':10s} {'log1p':10s} {sk:8.3f} {ku:8.3f}  (log(1+x), handles the zeros)")
        sk, ku = skew_kurt(np.sqrt(x))
        print(f"{'':18s} {'':10s} {'sqrt':10s} {sk:8.3f} {ku:8.3f}")
    else:
        print(f"{'':18s} {'':10s} {'log/sqrt':10s} {'skip (has negatives, e.g. northness -1..1)':>45s}")

    z = (x - x.mean()) / x.std()
    sk, ku = skew_kurt(z)
    print(f"{'':18s} {'':10s} {'z-score':10s} {sk:8.3f} {ku:8.3f}  (shape-preserving, sanity check only)")
    print()
