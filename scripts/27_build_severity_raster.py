"""
Derive the severity/refugia raster (band 18 of PortHills2017_stack.tif,
masked by valid_data band 19) as its own raster in the project gdb, with a
proper attribute table + class names, for the refugia map layout.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy
import numpy as np

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

stack = r"C:\Users\zhouy3d\Desktop\PortHills\data\PortHills2017_stack.tif"
gdb = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.gdb"

src = arcpy.Raster(stack)
lower_left = arcpy.Point(src.extent.XMin, src.extent.YMin)
cell_size = src.meanCellWidth
sr = src.spatialReference

arr = arcpy.RasterToNumPyArray(stack, nodata_to_value=np.nan)  # (22, rows, cols)
severity = arr[17]     # band 18, 1-indexed
valid = arr[18]        # band 19

out = np.where((valid == 1) & ~np.isnan(severity), severity, -1).astype(np.int32)

out_ras = arcpy.NumPyArrayToRaster(out, lower_left, cell_size, cell_size, value_to_nodata=-1)
arcpy.management.DefineProjection(out_ras, sr)

out_path = gdb + r"\Severity_2017_map"
out_ras.save(out_path)
print("saved", out_path)

arcpy.management.BuildRasterAttributeTable(out_path, "OVERWRITE")
arcpy.management.AddField(out_path, "ClassName", "TEXT", field_length=30)
NAMES = {0: "Unburned (refugia)", 1: "Low severity", 2: "Moderate severity", 3: "High severity"}
with arcpy.da.UpdateCursor(out_path, ["Value", "ClassName"]) as cur:
    for row in cur:
        row[1] = NAMES.get(row[0], "Unknown")
        cur.updateRow(row)

print("verify:")
with arcpy.da.SearchCursor(out_path, ["Value", "Count", "ClassName"]) as cur:
    for row in cur:
        print(row)
