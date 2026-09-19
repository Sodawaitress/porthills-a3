"""
US3 Second pass - 正态性(skewness/kurtosis) + 直方图。
判据(lab给的线): skewness < -1 或 > 1 = 非正态; kurtosis < -2 或 > 2 = 非正态。
"""
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

COLS = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
        "NDVI", "BSI", "NBR_pre", "elev", "slope", "northness"]

print(f"{'column':10s} {'skew':>8s} {'kurtosis':>10s}  normal?")
results = []
for c in COLS:
    sk = stats.skew(df[c])
    ku = stats.kurtosis(df[c])  # excess kurtosis (normal = 0), matches the |2| lab threshold
    non_normal = abs(sk) > 1 or abs(ku) > 2
    results.append((c, sk, ku, non_normal))
    flag = "NON-NORMAL" if non_normal else "ok"
    print(f"{c:10s} {sk:8.3f} {ku:10.3f}  {flag}")

print("\n非正态的列:", [r[0] for r in results if r[3]])

fig, axes = plt.subplots(3, 4, figsize=(18, 12))
for ax, c in zip(axes.flat, COLS):
    df[c].hist(ax=ax, bins=25)
    sk = df[c].skew()
    ku = df[c].kurtosis()
    ax.set_title(f"{c}  skew={sk:.2f} kurt={ku:.2f}", fontsize=10)
plt.tight_layout()
out_png = os.path.join(OUT_DIR, "histograms_normality.png")
plt.savefig(out_png, dpi=120)
print("\n直方图 ->", out_png)
