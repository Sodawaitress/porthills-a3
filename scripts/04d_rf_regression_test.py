"""
US4 补充 - 试试 RF 回归代替线性回归，能不能把 dNBR 的 R² 提上去。
用跟分类一样的 train/valid 空间分块 split，不是随机分，公平对比。
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

FEATURES = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
            "NDVI", "BSI", "elev", "slope", "northness"]
Y = "dNBR"

train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]

rf = RandomForestRegressor(n_estimators=500, random_state=42, oob_score=True)
rf.fit(train[FEATURES], train[Y])
print(f"OOB R² (训练集) = {rf.oob_score_:.4f}")

pred = rf.predict(valid[FEATURES])
r2 = r2_score(valid[Y], pred)
rmse = np.sqrt(mean_squared_error(valid[Y], pred))
mae = mean_absolute_error(valid[Y], pred)
print(f"验证集 R² = {r2:.4f}   RMSE = {rmse:.4f}   MAE = {mae:.4f}")

print("\n=== 加上 FuelClass(独热编码) ===")
dummies = pd.get_dummies(df["FuelClass"], prefix="cls")
df2 = pd.concat([df, dummies], axis=1)
feat2 = FEATURES + list(dummies.columns)
train2, valid2 = df2[df2["split"] == "train"], df2[df2["split"] == "valid"]

rf2 = RandomForestRegressor(n_estimators=500, random_state=42, oob_score=True)
rf2.fit(train2[feat2], train2[Y])
pred2 = rf2.predict(valid2[feat2])
r2_2 = r2_score(valid2[Y], pred2)
rmse2 = np.sqrt(mean_squared_error(valid2[Y], pred2))
print(f"OOB R² = {rf2.oob_score_:.4f}   验证集 R² = {r2_2:.4f}   RMSE = {rmse2:.4f}")

print("\n=== 对比总结 ===")
print(f"线性回归(清理后6变量):        验证集 R² = 0.413 (workflow.md记录)")
print(f"线性回归+FuelClass:           验证集 R² = 0.476")
print(f"RF回归(11个连续变量):         验证集 R² = {r2:.3f}")
print(f"RF回归+FuelClass:             验证集 R² = {r2_2:.3f}")

imp = pd.Series(rf2.feature_importances_, index=feat2).sort_values(ascending=False)
print("\n变量重要性(RF回归+FuelClass):")
print(imp.head(8))
