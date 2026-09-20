"""
US7 - refugia(未过火区)跟植被类型/地形的关系。
1. 全4类分类图(12号脚本产出)裁到真实火场边界(Port_Hills_2017_Fire_Boundary)
2. severity==0(dNBR<~100, Key&Benson未燃阈值)定义refugia
3. refugia比例按FuelClass交叉统计
4. refugia vs 过火区 的地形(elev/slope/northness)对比 + Welch t检验
"""
import arcpy
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

arcpy.env.overwriteOutput = True
gdb = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.gdb"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"
os.makedirs(OUT_DIR, exist_ok=True)

classified = gdb + r"\FuelClass_4class_map"
fire_boundary_src = r"C:\Users\zhouy3d\Desktop\PortHills\data\Port_Hills_2017_Fire_Boundary.shp"
stack_path = r"C:\Users\zhouy3d\Desktop\PortHills\data\PortHills2017_stack.tif"

nztm = arcpy.Describe(classified).spatialReference
fb_nztm = "in_memory\\fb_nztm"
arcpy.management.Project(fire_boundary_src, fb_nztm, nztm)
fb_dissolved = "in_memory\\fb_dissolved"
arcpy.management.Dissolve(fb_nztm, fb_dissolved)

clipped = gdb + r"\FuelClass_4class_map_clipped"
arcpy.management.Clip(classified, "#", clipped, fb_dissolved, "0", "ClippingGeometry", "MAINTAIN_EXTENT")

ras_classified = arcpy.Raster(clipped)
ext = ras_classified.extent
lower_left = arcpy.Point(ext.XMin, ext.YMin)
class_arr = arcpy.RasterToNumPyArray(clipped, nodata_to_value=0)
n_rows, n_cols = class_arr.shape
cell_size_str = "{} {}".format(ras_classified.meanCellWidth, ras_classified.meanCellHeight)

def get_band_aligned(source, band_num=None):
    if band_num:
        arcpy.management.MakeRasterLayer(source, "lyr_tmp", "#", "#", str(band_num))
        src = "lyr_tmp"
    else:
        src = source
    resampled = "in_memory\\rs_{}".format(band_num or "sev")
    arcpy.management.Resample(src, resampled, cell_size_str, "NEAREST")
    return arcpy.RasterToNumPyArray(resampled, lower_left, n_cols, n_rows, nodata_to_value=np.nan)

sev_arr = get_band_aligned(gdb + r"\severityClip")
band_names = ["pre_B2","pre_B3","pre_B4","pre_B5","pre_B6","pre_B7",
              "post_B2","post_B3","post_B4","post_B5","post_B6","post_B7",
              "NBR_pre","NBR_post","dNBR","NDVI","BSI","severity",
              "valid_data","elev","slope","northness"]
band_idx = {name: i + 1 for i, name in enumerate(band_names)}
elev = get_band_aligned(stack_path, band_idx["elev"])
slope = get_band_aligned(stack_path, band_idx["slope"])
northness = get_band_aligned(stack_path, band_idx["northness"])

valid = (class_arr > 0) & (~np.isnan(sev_arr)) & (sev_arr >= 0) & ~np.isnan(elev) & ~np.isnan(slope) & ~np.isnan(northness)
refugia = valid & (sev_arr == 0)
burned = valid & (sev_arr > 0)
print("有效像元:", valid.sum(), " refugia:", refugia.sum(), " 过火:", burned.sum())

CLASS_NAMES = {1: "pasture", 2: "gorse_broom", 3: "exotic_pine", 4: "broadleaf_scrub"}
print("\n=== refugia 占比 按 FuelClass ===")
refugia_pct = {}
for cid, name in CLASS_NAMES.items():
    mask = valid & (class_arr == cid)
    n_total = int(mask.sum())
    n_refugia = int((mask & (sev_arr == 0)).sum())
    pct = 100 * n_refugia / n_total if n_total > 0 else float("nan")
    refugia_pct[name] = pct
    print(f"  {name:16s} total={n_total:6d}px  refugia={n_refugia:6d}px  refugia%={pct:.1f}%")

print("\n=== refugia vs 过火区 地形对比(Welch t检验) ===")
terrain_results = {}
for name, arr in [("elevation_m", elev), ("slope_deg", slope), ("northness", northness)]:
    r_vals, b_vals = arr[refugia], arr[burned]
    t, p = stats.ttest_ind(r_vals, b_vals, equal_var=False)
    terrain_results[name] = (r_vals.mean(), b_vals.mean(), t, p)
    print(f"  {name}: refugia_mean={r_vals.mean():.2f}  burned_mean={b_vals.mean():.2f}  t={t:.2f}  p={p:.4g}")

# figure: refugia% by class bar chart + terrain boxplots
fig, axes = plt.subplots(1, 4, figsize=(18, 5))
axes[0].bar(refugia_pct.keys(), refugia_pct.values(), color="steelblue")
axes[0].set_title("Refugia % by FuelClass")
axes[0].set_ylabel("% unburned (severity=0)")
axes[0].tick_params(axis="x", rotation=30)

for ax, (name, arr) in zip(axes[1:], [("Elevation (m)", elev), ("Slope (deg)", slope), ("Northness", northness)]):
    ax.boxplot([arr[refugia], arr[burned]], tick_labels=["Refugia", "Burned"])
    ax.set_title(name)

plt.tight_layout()
out_png = os.path.join(OUT_DIR, "refugia_veg_terrain.png")
plt.savefig(out_png, dpi=130)
print("\n->", out_png)
