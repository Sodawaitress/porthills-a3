"""
US3 First pass - 空值/常数列/重复行 + 离群值(boxplot + IQR fences)。
跑在核心点表 scripts/PortHills_PointTable.csv 上（不是整幅栅格）。

跑法：ArcGIS Pro 自带的 python（有 pandas/scipy/matplotlib）：
  "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" 03_data_exploration_pass1.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"
import os
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV)
print("总行数:", len(df))

# 决定 #1 定的范围：6 个火前波段 + 主要指数 + 地形层
COLS = [
    "PortHills2017_stack_pre_B2", "PortHills2017_stack_pre_B3", "PortHills2017_stack_pre_B4",
    "PortHills2017_stack_pre_B5", "PortHills2017_stack_pre_B6", "PortHills2017_stack_pre_B7",
    "PortHills2017_stack_NDVI", "PortHills2017_stack_BSI", "PortHills2017_stack_NBR_pre",
    "PortHills2017_stack_elev", "PortHills2017_stack_slope", "PortHills2017_stack_northness",
]
SHORT = {c: c.replace("PortHills2017_stack_", "") for c in COLS}
df = df.rename(columns=SHORT)
COLS = list(SHORT.values())

print("\n=== 空值检查 ===")
nulls = df[COLS].isna().sum()
print(nulls[nulls > 0] if nulls.sum() > 0 else "没有空值")

print("\n=== 常数列检查（只有一个值，无预测力）===")
for c in df.columns:
    if df[c].nunique() == 1:
        print(f"  {c}: 常数列，值恒为 {df[c].iloc[0]} -> 应删除")

print("\n=== 重复行检查 ===")
dup = df.duplicated(subset=COLS).sum()
print(f"重复行数: {dup}")

print("\n=== First pass 离群值：IQR fences ===")
outlier_summary = []
for c in COLS:
    q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (df[c] < lo) | (df[c] > hi)
    n_out = mask.sum()
    outlier_summary.append((c, n_out, lo, hi))
    print(f"  {c}: {n_out} 个离群值 (下界{lo:.3f} 上界{hi:.3f})")

# 按离群值数量排序，最严重的排前面（配合 lab 教的"先删最严重的"顺序）
outlier_summary.sort(key=lambda r: -r[1])
print("\n按严重程度排序:", [(r[0], r[1]) for r in outlier_summary])

# 画箱线图：所有列放一张图，方便一眼比较
fig, axes = plt.subplots(3, 4, figsize=(18, 12))
for ax, c in zip(axes.flat, COLS):
    df.boxplot(column=c, by="FuelClass", ax=ax, rot=45)
    ax.set_title(c, fontsize=10)
    ax.set_xlabel("")
plt.suptitle("")
plt.tight_layout()
out_png = os.path.join(OUT_DIR, "boxplots_by_class.png")
plt.savefig(out_png, dpi=120)
print("\n箱线图 ->", out_png)
