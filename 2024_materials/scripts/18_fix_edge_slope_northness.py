"""
Fix: 2 points (FID 105, 118, both exotic_pine) got slope=-9999/northness=-9999
in PortHills2024_PointTable.csv - a literal sentinel value, not a proper null
(the earlier null-check passed because ArcGIS wrote -9999 into the field
instead of leaving it Null for these 2 cells).

Root cause: Slope/Aspect need a 3x3 neighbourhood to compute a gradient at
each cell. 14/09's DEM was clipped tight to the exact AOI polygon before
computing slope/aspect, so points close enough to the true AOI boundary lose
their neighbours off one side -> undefined gradient there, even though the
raw elevation/CHM (no neighbourhood needed) stayed valid at the same points.

Fix: extract DEM with a 100m buffer around the AOI (enough neighbourhood
context for a 1m-resolution 3x3 kernel), compute slope/aspect/northness on
that buffered extract, then re-sample only at the two broken points.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy
import pandas as pd
import numpy as np

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

wgs84 = arcpy.SpatialReference(4326)
nztm = arcpy.SpatialReference(2193)
COORDS_2024 = [[172.60428,-43.61764],[172.60529,-43.61721],[172.60505,-43.61653],[172.60564,-43.61569],[172.60610,-43.61558],[172.60807,-43.61769],[172.61197,-43.61568],[172.61070,-43.61552],[172.60941,-43.61457],[172.60867,-43.61489],[172.60668,-43.61380],[172.60871,-43.61330],[172.60692,-43.61304],[172.60518,-43.61099],[172.60693,-43.60866],[172.60713,-43.60674],[172.60642,-43.60636],[172.60708,-43.60469],[172.60665,-43.60264],[172.60855,-43.60466],[172.60844,-43.60515],[172.60982,-43.60600],[172.61121,-43.60618],[172.61047,-43.60368],[172.61218,-43.60349],[172.61001,-43.60273],[172.61079,-43.60230],[172.61191,-43.60294],[172.61420,-43.60116],[172.61494,-43.60147],[172.61798,-43.59947],[172.61921,-43.59974],[172.62244,-43.59915],[172.62393,-43.60035],[172.62358,-43.60087],[172.62545,-43.60294],[172.62985,-43.60295],[172.63050,-43.60151],[172.63652,-43.60387],[172.63774,-43.60489],[172.63776,-43.60571],[172.63641,-43.60709],[172.63476,-43.60670],[172.63485,-43.60941],[172.63563,-43.60967],[172.63670,-43.60906],[172.63957,-43.60992],[172.63668,-43.61210],[172.63523,-43.61228],[172.63466,-43.61155],[172.63531,-43.61042],[172.63413,-43.60965],[172.63349,-43.61021],[172.63385,-43.61073],[172.63183,-43.61032],[172.62732,-43.61071],[172.62778,-43.61144],[172.62691,-43.61119],[172.62889,-43.61307],[172.62861,-43.61383],[172.62682,-43.61214],[172.62402,-43.61144],[172.62075,-43.60950],[172.62049,-43.61034],[172.61881,-43.61032],[172.62013,-43.60924],[172.61946,-43.60894],[172.61893,-43.60963],[172.61825,-43.60948],[172.61825,-43.60837],[172.61729,-43.60873],[172.61578,-43.60716],[172.61514,-43.60710],[172.61410,-43.60803],[172.62064,-43.61339],[172.62257,-43.61640],[172.62178,-43.61724],[172.62221,-43.61801],[172.62192,-43.61823],[172.62394,-43.61953],[172.62463,-43.61944],[172.62457,-43.61992],[172.62534,-43.62044],[172.62719,-43.61983],[172.63010,-43.62138],[172.63040,-43.62245],[172.63198,-43.62404],[172.63037,-43.62425],[172.62845,-43.62382],[172.62866,-43.62441],[172.62784,-43.62437],[172.62761,-43.62491],[172.62744,-43.62443],[172.62648,-43.62665],[172.62738,-43.62670],[172.62711,-43.62524],[172.62767,-43.62572],[172.62941,-43.62586],[172.62950,-43.62644],[172.62869,-43.62614],[172.62954,-43.62704],[172.63124,-43.62735],[172.63165,-43.62768],[172.63106,-43.62804],[172.63331,-43.62925],[172.63358,-43.63055],[172.63423,-43.63059],[172.63376,-43.63127],[172.63210,-43.63070],[172.63228,-43.63158],[172.63149,-43.63166],[172.62931,-43.62981],[172.62854,-43.62789],[172.62644,-43.62749],[172.62455,-43.62597],[172.62257,-43.62555],[172.62112,-43.62341],[172.61866,-43.62418],[172.61593,-43.62584],[172.61518,-43.62494],[172.61139,-43.62482],[172.60973,-43.62583],[172.60812,-43.62461],[172.60901,-43.62383],[172.60687,-43.62291],[172.60542,-43.62387],[172.60485,-43.62299],[172.60656,-43.62251],[172.60744,-43.62103],[172.60428,-43.61764]]
array_2024 = arcpy.Array([arcpy.Point(x, y) for x, y in COORDS_2024])
poly = arcpy.Polygon(array_2024, wgs84).projectAs(nztm)
poly_buffered = poly.buffer(100)
arcpy.management.CopyFeatures(poly_buffered, "in_memory/aoi_buffered")

dem = r"J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DEM.tif"
dem_buf = arcpy.sa.ExtractByMask(dem, "in_memory/aoi_buffered")
aspect_buf = arcpy.sa.Aspect(dem_buf)
slope_buf = arcpy.sa.Slope(dem_buf, "DEGREE")
northness_buf = arcpy.sa.Con(aspect_buf == -1, 0,
                              arcpy.sa.Cos(aspect_buf * 3.14159265358979 / 180.0))

slope_buf_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\Slope_2024_buffered.tif"
north_buf_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\Northness_2024_buffered.tif"
slope_buf.save(slope_buf_path)
northness_buf.save(north_buf_path)

# ---- re-sample only the 2 broken points ----
pts_fc = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\TrainingPoints_2024_raw.shp"
broken_fids = [105, 118]
lyr = arcpy.management.MakeFeatureLayer(pts_fc, "broken_lyr",
    where_clause=f"FID IN ({','.join(str(f) for f in broken_fids)})")
print("points selected:", arcpy.management.GetCount(lyr)[0])

new_vals = {}
with arcpy.da.SearchCursor(lyr, ["FID", "SHAPE@XY"]) as cur:
    for fid, (x, y) in cur:
        pt = arcpy.PointGeometry(arcpy.Point(x, y), nztm)
        s = arcpy.management.GetCellValue(slope_buf_path, f"{x} {y}").getOutput(0)
        n = arcpy.management.GetCellValue(north_buf_path, f"{x} {y}").getOutput(0)
        new_vals[fid] = (float(s), float(n))
        print(f"FID {fid}: new slope={s}, new northness={n}")

# ---- patch the shapefile ----
with arcpy.da.UpdateCursor(pts_fc, ["FID", "slope", "northness"]) as cur:
    for row in cur:
        if row[0] in new_vals:
            row[1], row[2] = new_vals[row[0]]
            cur.updateRow(row)

# ---- patch the terrain CSV and the merged final point table ----
for csv_path in [r"C:\Users\zhouy3d\Desktop\a3\2024_materials\TrainingPoints_2024_terrain.csv",
                  r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv"]:
    df = pd.read_csv(csv_path)
    for fid, (s, n) in new_vals.items():
        df.loc[df["FID"] == fid, "slope"] = s
        df.loc[df["FID"] == fid, "northness"] = n
    df.to_csv(csv_path, index=False)
    print("patched:", csv_path)

# ---- verify ----
df = pd.read_csv(r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv")
print("\nremaining -9999 in slope:", (df["slope"] == -9999).sum())
print("remaining -9999 in northness:", (df["northness"] == -9999).sum())
print(df.loc[df["FID"].isin(broken_fids), ["FID", "FuelClass", "elev", "slope", "northness", "chm"]])
