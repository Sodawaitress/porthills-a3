"""
US5 - 光谱可分性：光谱曲线(6类火前波段均值) + Jeffries-Matusita(JM)指数。
JM: 0=完全重叠(分不开) ~ 2=完全分开。引用 Richards(2013) Remote Sensing
Digital Image Analysis 里的公式。
"""
import pandas as pd
import numpy as np
import itertools
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

BANDS = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7"]
FEATURES = BANDS + ["NDVI", "BSI"]  # 跟 kmeans 诊断用的特征空间一致
CLASSES = sorted(df["FuelClass"].unique())

def jm_distance(x1, x2):
    m1, m2 = x1.mean(axis=0), x2.mean(axis=0)
    c1, c2 = np.cov(x1, rowvar=False), np.cov(x2, rowvar=False)
    cavg = (c1 + c2) / 2
    dm = m1 - m2
    try:
        cavg_inv = np.linalg.inv(cavg)
    except np.linalg.LinAlgError:
        cavg_inv = np.linalg.pinv(cavg)
    term1 = (1 / 8) * dm @ cavg_inv @ dm.T
    sign1, logdet1 = np.linalg.slogdet(c1)
    sign2, logdet2 = np.linalg.slogdet(c2)
    signA, logdetA = np.linalg.slogdet(cavg)
    term2 = 0.5 * (logdetA - 0.5 * logdet1 - 0.5 * logdet2)
    B = term1 + term2
    jm = 2 * (1 - np.exp(-B))
    return jm

print("=== JM 可分性矩阵（越接近2越好分开，<1 算严重重叠）===")
jm_matrix = pd.DataFrame(index=CLASSES, columns=CLASSES, dtype=float)
for c in CLASSES:
    jm_matrix.loc[c, c] = 0.0

pairs = []
for c1, c2 in itertools.combinations(CLASSES, 2):
    x1 = df.loc[df["FuelClass"] == c1, FEATURES].values
    x2 = df.loc[df["FuelClass"] == c2, FEATURES].values
    jm = jm_distance(x1, x2)
    jm_matrix.loc[c1, c2] = jm
    jm_matrix.loc[c2, c1] = jm
    pairs.append((c1, c2, jm))

print(jm_matrix.round(2))

pairs.sort(key=lambda p: p[2])
print("\n最难分开的几对(JM最低):")
for c1, c2, jm in pairs[:5]:
    print(f"  {c1} vs {c2}: JM={jm:.3f}")

print("\n最好分开的几对(JM最高):")
for c1, c2, jm in pairs[-5:]:
    print(f"  {c1} vs {c2}: JM={jm:.3f}")

# 光谱曲线
fig, ax = plt.subplots(figsize=(8, 5))
for c in CLASSES:
    means = df.loc[df["FuelClass"] == c, BANDS].mean().values
    ax.plot(range(6), means, marker="o", label=c)
ax.set_xticks(range(6))
ax.set_xticklabels(["B2", "B3", "B4", "B5", "B6", "B7"])
ax.set_xlabel("Landsat band")
ax.set_ylabel("mean reflectance (pre-fire)")
ax.set_title("Per-class spectral profile (6 fuel classes)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
out_png = os.path.join(OUT_DIR, "spectral_profile_6class.png")
plt.savefig(out_png, dpi=130)
print("\n光谱曲线 ->", out_png)
