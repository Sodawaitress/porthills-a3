"""
US6 - 像元法 Random Forest 分类 + 混淆矩阵(OA/Kappa/PA/UA)。
训练/验证用之前定好的空间分块 split 字段，不是重新随机分。
"""
import pandas as pd
import numpy as np
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, cohen_kappa_score
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

FEATURES = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
            "NDVI", "BSI", "elev", "slope", "northness"]

train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
print(f"train={len(train)}  valid={len(valid)}")
print(train["FuelClass"].value_counts())

rf = RandomForestClassifier(n_estimators=500, random_state=42, oob_score=True)
rf.fit(train[FEATURES], train["FuelClass"])
print(f"\nOOB accuracy (on training set): {rf.oob_score_:.3f}")

pred = rf.predict(valid[FEATURES])
y_true = valid["FuelClass"].values

classes = sorted(df["FuelClass"].unique())
cm = confusion_matrix(y_true, pred, labels=classes)
cm_df = pd.DataFrame(cm, index=classes, columns=classes)
print("\n=== 混淆矩阵(行=真实类, 列=预测类) ===")
print(cm_df)

oa = accuracy_score(y_true, pred)
kappa = cohen_kappa_score(y_true, pred)
print(f"\nOverall Accuracy (OA) = {oa:.3f}")
print(f"Kappa = {kappa:.3f}")

print("\n=== 各类 Producer's / User's Accuracy ===")
for i, c in enumerate(classes):
    row_sum = cm[i, :].sum()  # 真实为c的总数
    col_sum = cm[:, i].sum()  # 预测为c的总数
    pa = cm[i, i] / row_sum if row_sum > 0 else np.nan
    ua = cm[i, i] / col_sum if col_sum > 0 else np.nan
    print(f"  {c:14s}  PA(漏分)={pa:.3f}  UA(错分)={ua:.3f}  (n_valid={row_sum})")

print("\n=== 变量重要性 ===")
imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
print(imp)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
im = axes[0].imshow(cm, cmap="Blues")
axes[0].set_xticks(range(len(classes))); axes[0].set_xticklabels(classes, rotation=45, ha="right")
axes[0].set_yticks(range(len(classes))); axes[0].set_yticklabels(classes)
axes[0].set_xlabel("Predicted"); axes[0].set_ylabel("True")
axes[0].set_title(f"Confusion Matrix  OA={oa:.2f} Kappa={kappa:.2f}")
for i in range(len(classes)):
    for j in range(len(classes)):
        axes[0].text(j, i, cm[i, j], ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black")
plt.colorbar(im, ax=axes[0], fraction=0.046)

imp.plot(kind="barh", ax=axes[1])
axes[1].set_title("Feature importance")
axes[1].invert_yaxis()

plt.tight_layout()
out_png = os.path.join(OUT_DIR, "rf_confusion_matrix.png")
plt.savefig(out_png, dpi=130)
print("\n->", out_png)
