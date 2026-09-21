"""
US6 补充 - SHAP 变量重要性，同一个4类最终RF模型(06c)上跑。
出处：Lundberg & Lee (2017) A Unified Approach to Interpreting Model
Predictions. references.md D组。
比裸Gini重要性多出：①方向(某波段高->更像哪一类，不只是"重要")
②每个类别分开看，不是全局一个排名 ③单点层面能看"为什么这个点被分成这类"。
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV)
df.columns = [c.replace("PortHills2017_stack_", "") for c in df.columns]
df4 = df[~df["FuelClass"].isin(["bare_rock", "cleared_pine"])].copy()

FEATURES = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
            "NDVI", "BSI", "elev", "slope", "northness"]
train = df4[df4["split"] == "train"]
valid = df4[df4["split"] == "valid"]

# same spec as 06c - same model, just adding an explainability layer on top
rf = RandomForestClassifier(n_estimators=500, random_state=42, oob_score=True)
rf.fit(train[FEATURES], train["FuelClass"])
classes = sorted(df4["FuelClass"].unique())
print("classes:", classes)

explainer = shap.TreeExplainer(rf)
sv = explainer.shap_values(valid[FEATURES])
# sklearn/shap API varies by version - normalise to a dict {class: (n_samples, n_features)}
if isinstance(sv, list):
    shap_by_class = {c: sv[i] for i, c in enumerate(rf.classes_)}
else:
    sv = np.asarray(sv)
    if sv.ndim == 3:
        shap_by_class = {c: sv[:, :, i] for i, c in enumerate(rf.classes_)}
    else:
        shap_by_class = {rf.classes_[0]: sv}

print("\n=== mean(|SHAP|) per feature per class (global importance, split by class) ===")
mean_abs = pd.DataFrame({c: np.abs(shap_by_class[c]).mean(axis=0) for c in rf.classes_},
                          index=FEATURES)
print(mean_abs.round(4))

overall = mean_abs.mean(axis=1).sort_values(ascending=False)
print("\n=== overall mean(|SHAP|) across classes (compare to 06c's Gini ranking) ===")
print(overall.round(4))

gini = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
print("\n=== Gini ranking (06c, for comparison) ===")
print(gini.round(4))
print("\nSHAP rank:", overall.index.tolist())
print("Gini rank:", gini.index.tolist())
print("same order:", overall.index.tolist() == gini.index.tolist())

# ---- bar chart: mean|SHAP| per feature, stacked/grouped by class ----
fig, ax = plt.subplots(figsize=(9, 6))
mean_abs.loc[overall.index].plot(kind="barh", stacked=True, ax=ax)
ax.set_xlabel("mean(|SHAP value|)")
ax.set_title("SHAP importance by class (4-class final RF model)")
ax.invert_yaxis()
plt.tight_layout()
out_png = os.path.join(OUT_DIR, "shap_importance_by_class.png")
plt.savefig(out_png, dpi=130)
print("\n->", out_png)

# ---- direction check: for the top feature, does high value push toward a
#      specific class or away from it? (this is what Gini alone can't tell you) ----
top_feat = overall.index[0]
print(f"\n=== direction check for top feature '{top_feat}' ===")
for c in rf.classes_:
    x = valid[top_feat].values
    y = shap_by_class[c][:, FEATURES.index(top_feat)]
    corr = np.corrcoef(x, y)[0, 1]
    direction = "higher value -> pushes TOWARD this class" if corr > 0 else "higher value -> pushes AWAY from this class"
    print(f"  {c:18s} corr(feature, shap)={corr:+.3f}  {direction}")
