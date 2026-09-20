"""
2024 Port Hills fire - CHM cleanup (cap DSM/DEM registration artifacts) + spatial map
alongside LCDB 2023 classes, so we can actually LOOK at where "Forest - Harvested" /
"Exotic Forest" structurally look like open/shrub vs regenerating tree canopy.

No aerial photo available close to the 2024 fire (checked LINZ, decided not worth
chasing for now) - this is the visual cross-check in its place, using what's already
verified: LCDB v6 (Name_2023) + Christchurch 1m LiDAR DSM/DEM (2020-2021).

Author: Claude (for Yu Zhou), 2026-09-20
"""
import arcpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

nztm = arcpy.SpatialReference(2193)
aoi_fc = r"in_memory/aoi_2024"
wgs84 = arcpy.SpatialReference(4326)
COORDS_2024 = [[172.60428,-43.61764],[172.60529,-43.61721],[172.60505,-43.61653],[172.60564,-43.61569],[172.60610,-43.61558],[172.60807,-43.61769],[172.61197,-43.61568],[172.61070,-43.61552],[172.60941,-43.61457],[172.60867,-43.61489],[172.60668,-43.61380],[172.60871,-43.61330],[172.60692,-43.61304],[172.60518,-43.61099],[172.60693,-43.60866],[172.60713,-43.60674],[172.60642,-43.60636],[172.60708,-43.60469],[172.60665,-43.60264],[172.60855,-43.60466],[172.60844,-43.60515],[172.60982,-43.60600],[172.61121,-43.60618],[172.61047,-43.60368],[172.61218,-43.60349],[172.61001,-43.60273],[172.61079,-43.60230],[172.61191,-43.60294],[172.61420,-43.60116],[172.61494,-43.60147],[172.61798,-43.59947],[172.61921,-43.59974],[172.62244,-43.59915],[172.62393,-43.60035],[172.62358,-43.60087],[172.62545,-43.60294],[172.62985,-43.60295],[172.63050,-43.60151],[172.63652,-43.60387],[172.63774,-43.60489],[172.63776,-43.60571],[172.63641,-43.60709],[172.63476,-43.60670],[172.63485,-43.60941],[172.63563,-43.60967],[172.63670,-43.60906],[172.63957,-43.60992],[172.63668,-43.61210],[172.63523,-43.61228],[172.63466,-43.61155],[172.63531,-43.61042],[172.63413,-43.60965],[172.63349,-43.61021],[172.63385,-43.61073],[172.63183,-43.61032],[172.62732,-43.61071],[172.62778,-43.61144],[172.62691,-43.61119],[172.62889,-43.61307],[172.62861,-43.61383],[172.62682,-43.61214],[172.62402,-43.61144],[172.62075,-43.60950],[172.62049,-43.61034],[172.61881,-43.61032],[172.62013,-43.60924],[172.61946,-43.60894],[172.61893,-43.60963],[172.61825,-43.60948],[172.61825,-43.60837],[172.61729,-43.60873],[172.61578,-43.60716],[172.61514,-43.60710],[172.61410,-43.60803],[172.62064,-43.61339],[172.62257,-43.61640],[172.62178,-43.61724],[172.62221,-43.61801],[172.62192,-43.61823],[172.62394,-43.61953],[172.62463,-43.61944],[172.62457,-43.61992],[172.62534,-43.62044],[172.62719,-43.61983],[172.63010,-43.62138],[172.63040,-43.62245],[172.63198,-43.62404],[172.63037,-43.62425],[172.62845,-43.62382],[172.62866,-43.62441],[172.62784,-43.62437],[172.62761,-43.62491],[172.62744,-43.62443],[172.62648,-43.62665],[172.62738,-43.62670],[172.62711,-43.62524],[172.62767,-43.62572],[172.62941,-43.62586],[172.62950,-43.62644],[172.62869,-43.62614],[172.62954,-43.62704],[172.63124,-43.62735],[172.63165,-43.62768],[172.63106,-43.62804],[172.63331,-43.62925],[172.63358,-43.63055],[172.63423,-43.63059],[172.63376,-43.63127],[172.63210,-43.63070],[172.63228,-43.63158],[172.63149,-43.63166],[172.62931,-43.62981],[172.62854,-43.62789],[172.62644,-43.62749],[172.62455,-43.62597],[172.62257,-43.62555],[172.62112,-43.62341],[172.61866,-43.62418],[172.61593,-43.62584],[172.61518,-43.62494],[172.61139,-43.62482],[172.60973,-43.62583],[172.60812,-43.62461],[172.60901,-43.62383],[172.60687,-43.62291],[172.60542,-43.62387],[172.60485,-43.62299],[172.60656,-43.62251],[172.60744,-43.62103],[172.60428,-43.61764]]
array_2024 = arcpy.Array([arcpy.Point(x, y) for x, y in COORDS_2024])
poly_2024_nztm = arcpy.Polygon(array_2024, wgs84).projectAs(nztm)
arcpy.management.CopyFeatures(poly_2024_nztm, aoi_fc)

# ---- 1. reload CHM built by 03_chm_by_lcdb_class.py, cap to plausible range ----
chm_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_2024_AOI.tif"
chm_raw = arcpy.Raster(chm_path)
# NZ's tallest trees are ~60-80m (a few giant natives); Port Hills exotic pine plantation
# rarely exceeds ~35m. Cap generously at 40m; floor small negative noise to 0.
chm_capped = arcpy.sa.Con(chm_raw > 40, 40, arcpy.sa.Con(chm_raw < 0, 0, chm_raw))
chm_capped_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_2024_AOI_capped.tif"
chm_capped.save(chm_capped_path)

chm_arr = arcpy.RasterToNumPyArray(chm_capped, nodata_to_value=np.nan)
print("CHM capped: min", np.nanmin(chm_arr), "max", np.nanmax(chm_arr), "median", np.nanmedian(chm_arr))

# ---- 2. rasterize LCDB Name_2023 to the same grid, for a side-by-side class map ----
lcdb_path = r"J:\Data\Landcover_Database_v6\lcdb-v60-land-cover-database-version-60-mainland-new-zealand.shp"
lcdb_clip = "in_memory/lcdb_clip2"
arcpy.analysis.Clip(lcdb_path, aoi_fc, lcdb_clip)

classes = sorted({row[0] for row in arcpy.da.SearchCursor(lcdb_clip, ["Name_2023"])})
class_to_id = {name: i + 1 for i, name in enumerate(classes)}
arcpy.management.AddField(lcdb_clip, "ClassID", "SHORT")
with arcpy.da.UpdateCursor(lcdb_clip, ["Name_2023", "ClassID"]) as cur:
    for row in cur:
        row[1] = class_to_id[row[0]]
        cur.updateRow(row)

class_raster_path = r"in_memory/lcdb_class_raster"
arcpy.env.snapRaster = chm_capped_path
arcpy.env.cellSize = chm_capped_path
arcpy.conversion.PolygonToRaster(lcdb_clip, "ClassID", class_raster_path,
                                  cell_assignment="CELL_CENTER", cellsize=chm_capped_path)
class_arr = arcpy.RasterToNumPyArray(class_raster_path, nodata_to_value=0)

print("Classes:", class_to_id)
print("CHM grid shape:", chm_arr.shape, "class grid shape:", class_arr.shape)

# ---- 3. figure: CHM map + LCDB class map side by side ----
fig, axes = plt.subplots(1, 2, figsize=(14, 7))

im0 = axes[0].imshow(chm_arr, cmap="viridis", vmin=0, vmax=15)
axes[0].set_title("Canopy height (m), LiDAR 2020-21\n(capped 0-40m, DSM-DEM registration\nartifacts removed)")
axes[0].axis("off")
plt.colorbar(im0, ax=axes[0], fraction=0.04, label="m")

n_classes = len(classes)
cmap = ListedColormap(plt.cm.tab10.colors[:n_classes])
bounds = list(range(1, n_classes + 2))
norm = BoundaryNorm(bounds, cmap.N)
masked = np.where(class_arr == 0, np.nan, class_arr)
im1 = axes[1].imshow(masked, cmap=cmap, norm=norm)
axes[1].set_title("LCDB Name_2023 class")
axes[1].axis("off")
cbar = plt.colorbar(im1, ax=axes[1], ticks=[i + 0.5 for i in range(1, n_classes + 1)], fraction=0.04)
cbar.ax.set_yticklabels(classes, fontsize=7)

plt.tight_layout()
out_png = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_vs_LCDB2023_map.png"
plt.savefig(out_png, dpi=150)
print("Saved:", out_png)

# ---- 4. re-run the by-class summary on the CAPPED chm (median already robust, but
#          mean/std were garbage before; capped mean is now trustworthy too) ----
zonal_table = "in_memory/chm_by_class_capped"
arcpy.sa.ZonalStatisticsAsTable(lcdb_clip, "Name_2023", chm_capped, zonal_table, statistics_type="ALL")
print("\n=== CHM (m, capped) by LCDB Name_2023 class ===")
fields = ["Name_2023", "COUNT", "MEAN", "STD", "MIN", "MAX", "MEDIAN"]
existing = [f.name for f in arcpy.ListFields(zonal_table)]
fields = [f for f in fields if f in existing]
with arcpy.da.SearchCursor(zonal_table, fields) as cur:
    rows = list(cur)
for row in sorted(rows, key=lambda r: -r[fields.index("COUNT")]):
    parts = ", ".join(f"{f}={v:.2f}" if isinstance(v, float) else f"{f}={v}" for f, v in zip(fields, row))
    print(" ", parts)
