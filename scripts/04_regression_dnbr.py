"""
US4 - dNBR 线性回归（决定#2 选①）+ VIF + 类别变量增量检验。
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

PRED = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7", "NDVI", "BSI",
        "elev", "slope", "northness"]
Y = "dNBR"

print("=== 相关表：各预测变量 与 dNBR 的相关系数 ===")
corr = df[PRED + [Y]].corr()[Y].drop(Y).sort_values(key=abs, ascending=False)
print(corr)

print("\n=== VIF（多重共线性检查，>7.5 = 冗余）===")
X_vif = sm.add_constant(df[PRED])
vif = pd.Series(
    [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])],
    index=X_vif.columns
).drop("const").sort_values(ascending=False)
print(vif)

print("\n=== 模型①：dNBR ~ 连续变量(波段+指数+地形) ===")
X1 = sm.add_constant(df[PRED])
m1 = sm.OLS(df[Y], X1).fit()
print(f"R² = {m1.rsquared:.4f}   调整R² = {m1.rsquared_adj:.4f}")
resid1 = m1.resid
rmse1 = np.sqrt((resid1 ** 2).mean())
mae1 = resid1.abs().mean()
print(f"RMSE = {rmse1:.4f}   MAE = {mae1:.4f}")

print("\n=== 模型②：模型① + FuelClass 哑变量 ===")
dummies = pd.get_dummies(df["FuelClass"], prefix="cls", drop_first=True, dtype=float)
X2 = sm.add_constant(pd.concat([df[PRED], dummies], axis=1))
m2 = sm.OLS(df[Y], X2).fit()
print(f"R² = {m2.rsquared:.4f}   调整R² = {m2.rsquared_adj:.4f}")
resid2 = m2.resid
rmse2 = np.sqrt((resid2 ** 2).mean())
mae2 = resid2.abs().mean()
print(f"RMSE = {rmse2:.4f}   MAE = {mae2:.4f}")

print(f"\n=== 对比：加 FuelClass 类别变量后，R² 提升了 {m2.rsquared - m1.rsquared:.4f} ===")

# F-test: 加进去的这组类别变量整体上是否显著提升了模型
f_test = m2.compare_f_test(m1)
print(f"F检验(类别变量整体是否显著): F={f_test[0]:.3f}, p={f_test[1]:.4f}")
