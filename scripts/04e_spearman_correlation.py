"""
US4 补充 - Spearman 秩相关，跟04号脚本的 Pearson 并排比较。
方法出处：Domingo et al. (2020) Remote Sensing 12(21):3660（references.md E3）
用 Spearman 而不是 Pearson 选特征，理由：不要求线性/正态，抓单调关系——
跟 US3 Second Pass 已经发现的"72组里19组按类别算非正态"直接呼应，比只用
Pearson(假设线性关系)更站得住。
"""
import pandas as pd
import numpy as np
from scipy import stats

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

PRED = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7", "NDVI", "BSI",
        "elev", "slope", "northness"]
Y = "dNBR"
# dNBR has 16 nulls (cleared_pine points that hit post-fire cloud, see workflow.md
# US2/method records) - scipy.stats needs clean arrays (unlike pandas .corr(), which
# silently does pairwise-deletion). Drop those rows, same effective set 04's .corr() used.
df = df.dropna(subset=[Y] + PRED)
n = len(df)

rows = []
for p in PRED:
    pear_r, pear_p = stats.pearsonr(df[p], df[Y])
    spear_r, spear_p = stats.spearmanr(df[p], df[Y])
    rows.append((p, pear_r, pear_p, spear_r, spear_p, abs(spear_r) - abs(pear_r)))

out = pd.DataFrame(rows, columns=["var", "pearson_r", "pearson_p", "spearman_r", "spearman_p", "abs_diff"])
out = out.sort_values("abs_diff", key=abs, ascending=False)
pd.set_option("display.width", 120)
print(f"n = {n}\n")
print(out.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

print("\n=== rank order change (|r| descending) ===")
pear_rank = out.reindex(out["pearson_r"].abs().sort_values(ascending=False).index)["var"].tolist()
spear_rank = out.reindex(out["spearman_r"].abs().sort_values(ascending=False).index)["var"].tolist()
print("Pearson rank :", pear_rank)
print("Spearman rank:", spear_rank)
print("same order:", pear_rank == spear_rank)

biggest = out.iloc[0]
print(f"\nbiggest diff: {biggest['var']}  Pearson r={biggest['pearson_r']:.3f}  Spearman r={biggest['spearman_r']:.3f}  diff={biggest['abs_diff']:.3f}")
