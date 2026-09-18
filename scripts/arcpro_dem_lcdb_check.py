"""
US1.2 辅助 - 用 arcpy 把三层(2015航片 / 1m LiDAR 山体阴影 / LCDB)叠进
PortHills2017.aprx,做个快速目视核对(航片能不能对上 LCDB 边界、地形细不细)。

跑法：必须用 ArcGIS Pro 自带的 python，不是系统 python。
  "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" arcpro_dem_lcdb_check.py

这不是替代 ArcGIS Pro 界面操作——只是把重复的几步（裁剪/建阴影/加图层/调符号）
写成脚本，好复现、好检查。GUI 版对应步骤见聊天记录里的"最简单"那版。
"""
import arcpy

# ==== PATHS (edit per machine) ====
PROJECT_HOME = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017"
AOI          = rf"{PROJECT_HOME}\a2\a2map1\vector\PortHills_AOI.shp"
AERIAL_2015  = rf"{PROJECT_HOME}\a2\a2map1\raster\PortHills_Aerial03m_2015.tif"
LCDB_FC      = rf"{PROJECT_HOME}\PortHills2017.gdb\lcdbPorthills"          # 已裁好、带 Class_2012 字段
LIDAR_DEM_1M = r"J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DEM.tif"
OUT_DEM_1M   = rf"{PROJECT_HOME}\a3\raster\PortHills_DEM1m_LiDAR.tif"
OUT_HS_1M    = rf"{PROJECT_HOME}\a3\raster\PortHills_HS1m_LiDAR.tif"
APRX_PATH    = rf"{PROJECT_HOME}\PortHills2017.aprx"
# ==================================

# ---- 1. 裁 1m LiDAR DEM 到 AOI（保留原生 1m 分辨率）----
ext = arcpy.Describe(AOI).extent
arcpy.management.Clip(
    LIDAR_DEM_1M,
    f"{ext.XMin} {ext.YMin} {ext.XMax} {ext.YMax}",
    OUT_DEM_1M,
    AOI,
    "-9999",
    "ClippingGeometry",
    "NO_MAINTAIN_EXTENT",
)

# ---- 2. 验证：范围内不能有大片 NoData，高程范围要合理（Port Hills 顶 ~500m）----
arcpy.management.CalculateStatistics(OUT_DEM_1M)
print("1m DEM min/max:",
      arcpy.management.GetRasterProperties(OUT_DEM_1M, "MINIMUM")[0],
      arcpy.management.GetRasterProperties(OUT_DEM_1M, "MAXIMUM")[0])
print("anyNoData:", arcpy.management.GetRasterProperties(OUT_DEM_1M, "ANYNODATA")[0])

# ---- 3. 建山体阴影（需要先在 Project > Licensing 里勾 Spatial Analyst）----
arcpy.CheckOutExtension("Spatial")
from arcpy.sa import Hillshade
Hillshade(OUT_DEM_1M, 315, 45).save(OUT_HS_1M)

# ---- 4. 打开工程，建一个新地图页做核对（不动原来的 "Map"）----
aprx = arcpy.mp.ArcGISProject(APRX_PATH)
for m in list(aprx.listMaps()):
    if m.name == "A3_DataCheck":
        aprx.deleteItem(m)

new_map = aprx.createMap("A3_DataCheck", "Map")
new_map.spatialReference = arcpy.Describe(AOI).spatialReference

# 只加三层本地数据，不带默认底图（不然会从图幅缝隙里露出来）
for lyr in list(new_map.listLayers()):
    new_map.removeLayer(lyr)

lyr_aerial = new_map.addDataFromPath(AERIAL_2015)
lyr_hs = new_map.addDataFromPath(OUT_HS_1M)
lyr_lcdb = new_map.addDataFromPath(LCDB_FC)

# 山体阴影：灰阶拉伸（不设的话 ArcGIS 有时会当成"离散值"渲染成乱七八糟的彩色）
sym_hs = lyr_hs.symbology
sym_hs.updateColorizer("RasterStretchColorizer")
sym_hs.colorizer.stretchType = "StandardDeviation"
ramps = aprx.listColorRamps("Black to White")
if ramps:
    sym_hs.colorizer.colorRamp = ramps[0]
lyr_hs.symbology = sym_hs
lyr_hs.transparency = 45

# LCDB：按 Class_2012 分类上色（这才是报告要用的版本；只想看边界对不对齐就注释掉这段，
# 换成 sym.renderer.symbol.applySymbolFromGallery('Black Outline (1pt)') 只留黑框）
sym_lcdb = lyr_lcdb.symbology
sym_lcdb.updateRenderer("UniqueValueRenderer")
sym_lcdb.renderer.fields = ["Class_2012"]
lyr_lcdb.symbology = sym_lcdb
lyr_lcdb.transparency = 35

# 叠放顺序：航片(底) -> 阴影(中) -> LCDB(顶)
new_map.moveLayer(lyr_lcdb, lyr_hs, "BEFORE")

aprx.save()
print("done -> 打开 PortHills2017.aprx，看 'A3_DataCheck' 那个地图页")
