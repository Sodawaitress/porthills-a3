"""
US4 - 散点图：清理后保留的 6 个预测变量 各自 vs dNBR，带趋势线+R²。
"""
import pandas as pd
import numpy as np
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

PRED = ["pre_B5", "pre_B7", "NDVI", "elev", "slope", "northness"]
Y = "dNBR"

fig, axes = plt.subplots(2, 3, figsize=(15, 9))
for ax, c in zip(axes.flat, PRED):
    x = df[c].values
    y = df[Y].values
    ax.scatter(x, y, s=12, alpha=0.5)

    slope, intercept, r, p, se = stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, slope * xs + intercept, color="red", linewidth=1.5)
    ax.set_title(f"{c}  R²={r**2:.3f}  p={p:.4f}", fontsize=10)
    ax.set_xlabel(c)
    ax.set_ylabel("dNBR")

plt.tight_layout()
out_png = os.path.join(OUT_DIR, "scatter_dnbr.png")
plt.savefig(out_png, dpi=120)
print("saved ->", out_png)
