import pandas as pd
from scipy import stats

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

COLS = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
        "NDVI", "BSI", "NBR_pre", "elev", "slope", "northness"]

flags = []
for cls, g in df.groupby("FuelClass"):
    n = len(g)
    for c in COLS:
        sk = stats.skew(g[c])
        ku = stats.kurtosis(g[c])
        non_normal = abs(sk) > 1 or abs(ku) > 2
        if non_normal:
            flags.append((cls, c, n, sk, ku))

print(f"{'class':14s} {'var':10s} {'n':>4s} {'skew':>8s} {'kurt':>8s}")
for cls, c, n, sk, ku in flags:
    print(f"{cls:14s} {c:10s} {n:4d} {sk:8.3f} {ku:8.3f}")

print(f"\n共 {len(flags)} 个 (类别,变量) 组合非正态，总组合数 {df['FuelClass'].nunique() * len(COLS)}")

import collections
by_class = collections.Counter(f[0] for f in flags)
by_var = collections.Counter(f[1] for f in flags)
print("按类别汇总非正态次数:", dict(by_class))
print("按变量汇总非正态次数:", dict(by_var))

print("\n各类别样本量(小样本偏度/峰度本来就不稳):")
print(df.groupby("FuelClass").size())
