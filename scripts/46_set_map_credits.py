# -*- coding: utf-8 -*-
"""Set the source block at the foot of the final maps to sources + projection
only, then export them to exploration/map_final/.

Saves the change into PortHills2017.aprx when Pro is closed; while Pro holds
the file lock it only exports (the aprx keeps the old text until re-run).
"""
import os, arcpy

APRX = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.aprx"
OUT = r"C:\Users\zhouy3d\Desktop\a3\exploration\map_final"
BASEMAP = "Basemap: Eagle Technology, LINZ, StatsNZ, NIWA."
BOUNDARY = "2017 fire boundary (CDEM/ECan)"
CRS = "Projection: NZGD2000 / New Zealand Transverse Mercator 2000 (EPSG:2193)."

CREDITS = {
    # layout name: (export name, source lines)
    "V2_CVDsafe": ("Map1_FuelClass_V2", [
        "Data: Landsat 8 OLI Collection 2 Level-2 (USGS); LINZ 2015-16 aerial photography; LCDB;",
        "Hansen Global Forest Change v1.11 (2023); " + BOUNDARY + ". " + BASEMAP, CRS]),
    "Map2_Refugia": ("Map2_Refugia", [
        "Data: Landsat 8 OLI Collection 2 Level-2 (USGS); " + BOUNDARY + ". " + BASEMAP, CRS]),
    "Map3_DataCleaning": ("Map3_DataCleaning", [
        "Data: Landsat 8 OLI Collection 2 Level-2 (USGS); " + BOUNDARY + ". " + BASEMAP, CRS]),
}

p = arcpy.mp.ArcGISProject(APRX)
for lname, (fn, lines) in CREDITS.items():
    lo = p.listLayouts(lname)[0]
    lo.listElements("TEXT_ELEMENT", "Credits")[0].text = "\n".join(lines)
    lo.exportToPNG(os.path.join(OUT, fn + ".png"), resolution=300)
    lo.exportToPDF(os.path.join(OUT, fn + ".pdf"), resolution=300)
    print("ok", lname)
try:
    p.save()
    print("saved into aprx")
except OSError:
    print("aprx is open in ArcGIS Pro: exported only, NOT saved -- close Pro and re-run")
