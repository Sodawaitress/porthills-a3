"""
US4 补充 - RBR(Relative Burn Ratio) 并列回归，对照 04 号脚本的 dNBR 回归。
RBR = dNBR / (NBR_pre + 1.001)，出处 Parks et al. (2014) Remote Sensing 6(3),
1827-1844, "A New Metric for Quantifying Burn Severity: The Relative dNBR"。
references.md C组。

不是换掉 dNBR，是并列一版看两者结果差多少——dNBR 是原始烧毁强度，RBR 是拿
火前生物量(NBR_pre)做分母校正过的版本，理论上更适合植被密度不均匀的地方
(本项目6类燃料密度差异很大，从bare_rock到exotic_pine密林，正是RBR设计要
解决的场景)。
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

df["RBR"] = df["dNBR"] / (df["NBR_pre"] + 1.001)

PRED = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7", "NDVI", "BSI",
        "elev", "slope", "northness"]
df_clean = df.dropna(subset=["dNBR", "RBR"] + PRED)
print(f"n = {len(df_clean)} (same rows as 04's dNBR regression)")

for Y in ["dNBR", "RBR"]:
    print(f"\n{'='*20} Y = {Y} {'='*20}")
    print(f"range: {df_clean[Y].min():.3f} to {df_clean[Y].max():.3f}, mean={df_clean[Y].mean():.3f}")

    X = sm.add_constant(df_clean[PRED])
    m = sm.OLS(df_clean[Y], X).fit()
    resid = m.resid
    rmse = np.sqrt((resid ** 2).mean())
    mae = resid.abs().mean()
    print(f"R² = {m.rsquared:.4f}   adj R² = {m.rsquared_adj:.4f}   RMSE = {rmse:.4f}   MAE = {mae:.4f}")

    dummies = pd.get_dummies(df_clean["FuelClass"], prefix="cls", drop_first=True, dtype=float)
    X2 = sm.add_constant(pd.concat([df_clean[PRED], dummies], axis=1))
    m2 = sm.OLS(df_clean[Y], X2).fit()
    print(f"+ FuelClass dummies: R² = {m2.rsquared:.4f}   adj R² = {m2.rsquared_adj:.4f}")
    f_test = m2.compare_f_test(m)
    print(f"F-test (FuelClass group significant?): F={f_test[0]:.3f}, p={f_test[1]:.4f}")

    corr = df_clean[PRED + [Y]].corr()[Y].drop(Y).sort_values(key=abs, ascending=False)
    print(f"\ntop 3 correlates with {Y}:")
    print(corr.head(3))

