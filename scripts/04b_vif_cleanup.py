"""
US4 - 按 lab 教的规矩迭代清理 VIF：每轮删掉 VIF 最高的一个变量，重算，
直到全部 <= 7.5。
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
THRESH = 7.5

removed = []
current = list(PRED)
round_n = 0
while True:
    round_n += 1
    X = sm.add_constant(df[current])
    vif = pd.Series(
        [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
        index=X.columns
    ).drop("const")
    worst = vif.idxmax()
    print(f"第{round_n}轮 最高VIF: {worst}={vif[worst]:.1f}  (剩{len(current)}个变量)")
    if vif[worst] <= THRESH:
        print("全部达标，停止")
        break
    current.remove(worst)
    removed.append(worst)

print("\n删掉的变量(按删除顺序):", removed)
print("保留的变量:", current)

print("\n=== 最终VIF ===")
X = sm.add_constant(df[current])
vif = pd.Series(
    [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
    index=X.columns
).drop("const").sort_values(ascending=False)
print(vif)

print("\n=== 清理后模型①：连续变量 ===")
X1 = sm.add_constant(df[current])
m1 = sm.OLS(df[Y], X1).fit()
print(f"R² = {m1.rsquared:.4f}   调整R² = {m1.rsquared_adj:.4f}")
print(f"RMSE = {np.sqrt((m1.resid**2).mean()):.4f}   MAE = {m1.resid.abs().mean():.4f}")
print(m1.params)

print("\n=== 清理后模型②：+ FuelClass ===")
dummies = pd.get_dummies(df["FuelClass"], prefix="cls", drop_first=True, dtype=float)
X2 = sm.add_constant(pd.concat([df[current], dummies], axis=1))
m2 = sm.OLS(df[Y], X2).fit()
print(f"R² = {m2.rsquared:.4f}   调整R² = {m2.rsquared_adj:.4f}")
print(f"RMSE = {np.sqrt((m2.resid**2).mean()):.4f}   MAE = {m2.resid.abs().mean():.4f}")
f_test = m2.compare_f_test(m1)
print(f"F检验(类别变量整体显著性): F={f_test[0]:.3f}, p={f_test[1]:.4f}")
