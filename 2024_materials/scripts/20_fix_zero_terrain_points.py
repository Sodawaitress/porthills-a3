"""
Fix: 3 pasture points (FID 2, 11, 32) have elev=slope=northness=chm=0 all
at once - while their S2-derived NDVI etc look completely normal (healthy
pasture, ~0.83-0.86). All-four-terrain-vars-exactly-0 is the signature of
"this point technically fell outside the AOI-clipped raster's valid extent by
a hair" (pasture_2024.shp was built from LCDB-clip-to-AOI, a DIFFERENT
polygon computation than the raster's own AOI mask - a sub-pixel vertex
mismatch between the two is enough to push an edge point outside the masked
raster's data footprint), not real sea-level pasture (this AOI's pasture is
at 260-454m per the other 47 points).

Fix: sample straight from the RAW, unclipped LINZ DEM/DSM (full Christchurch
extent, no AOI-clip edge to fall outside of) at these 3 points' exact
coordinates, recomputing slope/aspect/northness/chm locally around them.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
nztm = arcpy.SpatialReference(2193)

pts_fc = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\TrainingPoints_2024_raw.shp"
broken_fids = [2, 11, 32]

dem_raw = r"J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DEM.tif"
dsm_raw = r"J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DSM.tif"

lyr = arcpy.management.MakeFeatureLayer(pts_fc, "broken_lyr",
    where_clause=f"FID IN ({','.join(str(f) for f in broken_fids)})")
print("points selected:", arcpy.management.GetCount(lyr)[0])

coords = {}
with arcpy.da.SearchCursor(lyr, ["FID", "SHAPE@XY"]) as cur:
    for fid, xy in cur:
        coords[fid] = xy

new_vals = {}
for fid, (x, y) in coords.items():
    # small local extract (200m box) around the point, on the RAW (unclipped) DEM/DSM,
    # so slope/aspect have full neighbourhood + the point is nowhere near a clip edge
    box = arcpy.Extent(x - 100, y - 100, x + 100, y + 100)
    arcpy.env.extent = box
    dem_local = arcpy.sa.Raster(dem_raw)

    elev_val = float(arcpy.management.GetCellValue(dem_raw, f"{x} {y}").getOutput(0))
    dsm_val = float(arcpy.management.GetCellValue(dsm_raw, f"{x} {y}").getOutput(0))
    chm_val = dsm_val - elev_val

    slope_ras = arcpy.sa.Slope(dem_local, "DEGREE")
    aspect_ras = arcpy.sa.Aspect(dem_local)
    slope_val = float(arcpy.management.GetCellValue(slope_ras, f"{x} {y}").getOutput(0))
    aspect_val = float(arcpy.management.GetCellValue(aspect_ras, f"{x} {y}").getOutput(0))
    import math
    north_val = 0.0 if aspect_val == -1 else math.cos(math.radians(aspect_val))

    new_vals[fid] = (elev_val, slope_val, north_val, chm_val)
    print(f"FID {fid}: elev={elev_val:.2f} slope={slope_val:.2f} northness={north_val:.3f} chm={chm_val:.2f}")

arcpy.env.extent = None

with arcpy.da.UpdateCursor(pts_fc, ["FID", "elev", "slope", "northness", "chm"]) as cur:
    for row in cur:
        if row[0] in new_vals:
            row[1], row[2], row[3], row[4] = new_vals[row[0]]
            cur.updateRow(row)

import pandas as pd
for csv_path in [r"C:\Users\zhouy3d\Desktop\a3\2024_materials\TrainingPoints_2024_terrain.csv",
                  r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv"]:
    df = pd.read_csv(csv_path)
    for fid, (e, s, n, c) in new_vals.items():
        df.loc[df["FID"] == fid, "elev"] = e
        df.loc[df["FID"] == fid, "slope"] = s
        df.loc[df["FID"] == fid, "northness"] = n
        df.loc[df["FID"] == fid, "chm"] = c
    df.to_csv(csv_path, index=False)
    print("patched:", csv_path)

df = pd.read_csv(r"C:\Users\zhouy3d\Desktop\a3\2024_materials\PortHills2024_PointTable.csv")
print("\nremaining zero-elev points:", (df["elev"] == 0).sum())
print(df.loc[df["FID"].isin(broken_fids), ["FID", "FuelClass", "elev", "slope", "northness", "chm", "NDVI"]])
