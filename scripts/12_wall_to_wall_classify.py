"""
US7/US9 - 把US6最终版4类RF分类器(pasture/gorse_broom/exotic_pine/broadleaf_scrub)
套到整个栅格上，出一张全区域燃料分类图。用全部176个点重新训练(不再切train/valid,
US6已经用切分验证过精度=OA0.684/Kappa0.579，这里是要做最终产出图,用全部数据训练
效果最好)。

bare_rock/cleared_pine 不进分类，最后作为已知信息叠加：
  - cleared_pine_real: 真实边界，直接叠加覆盖分类结果
  - bare_rock: 没有边界，图上留白/标注"未知覆盖"，不假装有答案
"""
import arcpy
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

stack_path = r"C:\Users\zhouy3d\Desktop\PortHills\data\PortHills2017_stack.tif"
csv_path = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
out_raster = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.gdb\FuelClass_4class_map"

FEATURES = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
            "NDVI", "BSI", "elev", "slope", "northness"]
CLASS_NAMES = ["pasture", "gorse_broom", "exotic_pine", "broadleaf_scrub"]
CLASS_TO_INT = {c: i + 1 for i, c in enumerate(CLASS_NAMES)}  # 1-4, 0=nodata

# ---- train on ALL 176 4-class points (no train/valid split -- this is the
#      final production model; accuracy already reported from 06c's split test) ----
df = pd.read_csv(csv_path)
df.columns = [c.replace("PortHills2017_stack_", "") for c in df.columns]
df4 = df[~df["FuelClass"].isin(["bare_rock", "cleared_pine"])].copy()
rf = RandomForestClassifier(n_estimators=500, random_state=42)
rf.fit(df4[FEATURES], df4["FuelClass"])
print("trained on", len(df4), "points:", df4["FuelClass"].value_counts().to_dict())

# ---- load stack bands as arrays ----
band_names = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
              "post_B2", "post_B3", "post_B4", "post_B5", "post_B6", "post_B7",
              "NBR_pre", "NBR_post", "dNBR", "NDVI", "BSI", "severity",
              "valid_data", "elev", "slope", "northness"]
desc = arcpy.Describe(stack_path)
ras_obj = arcpy.Raster(stack_path)
rows, cols = ras_obj.height, ras_obj.width
print("raster size:", rows, "x", cols)

raster = arcpy.RasterToNumPyArray(stack_path, nodata_to_value=np.nan)  # shape (bands, rows, cols)
band_idx = {name: i for i, name in enumerate(band_names)}

feat_stack = np.stack([raster[band_idx[f]] for f in FEATURES], axis=-1)  # (rows, cols, n_features)
flat = feat_stack.reshape(-1, len(FEATURES))

valid_mask = ~np.isnan(flat).any(axis=1)
print("valid pixels:", valid_mask.sum(), "/", flat.shape[0])

pred = np.zeros(flat.shape[0], dtype=np.uint8)
pred[valid_mask] = [CLASS_TO_INT[c] for c in rf.predict(flat[valid_mask])]
pred_2d = pred.reshape(rows, cols)

# write out as raster, matching the stack's extent/cellsize/SR
lower_left = arcpy.Point(desc.extent.XMin, desc.extent.YMin)
out_ras = arcpy.NumPyArrayToRaster(pred_2d, lower_left, ras_obj.meanCellWidth, ras_obj.meanCellHeight, value_to_nodata=0)
arcpy.management.DefineProjection(out_ras, desc.spatialReference)
out_ras.save(out_raster)
print("wrote ->", out_raster)

print("\n像元数按类统计:")
vals, counts = np.unique(pred_2d[pred_2d > 0], return_counts=True)
for v, c in zip(vals, counts):
    name = [k for k, vv in CLASS_TO_INT.items() if vv == v][0]
    print(f"  {name:16s} {c:6d} px  ({c*0.09:.2f} ha)")
