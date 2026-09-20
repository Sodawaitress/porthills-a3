"""
Fix: 07_finalize_cleared_pine_2024.py used the 2012 pine footprint (225.5ha)
for cleared_pine/exotic_pine, while 10_finalize_remaining_classes.py used 2023
labels for the other 3 classes -> double counting wherever LCDB itself already
relabelled former pine to Gorse/Broom etc between 2012 and 2023 (total came to
538.4ha vs AOI 467.3ha). Redo cleared_pine/exotic_pine on the 2023 "Exotic
Forest + Forest - Harvested" footprint (154.5ha) instead, consistent with the
other 3 classes, then re-check the totals sum to ~AOI.

Author: Claude (for Yu Zhou), 2026-09-20
"""
import json
import arcpy

arcpy.env.overwriteOutput = True
wgs84 = arcpy.SpatialReference(4326)
nztm = arcpy.SpatialReference(2193)
COORDS_2024 = [[172.60428,-43.61764],[172.60529,-43.61721],[172.60505,-43.61653],[172.60564,-43.61569],[172.60610,-43.61558],[172.60807,-43.61769],[172.61197,-43.61568],[172.61070,-43.61552],[172.60941,-43.61457],[172.60867,-43.61489],[172.60668,-43.61380],[172.60871,-43.61330],[172.60692,-43.61304],[172.60518,-43.61099],[172.60693,-43.60866],[172.60713,-43.60674],[172.60642,-43.60636],[172.60708,-43.60469],[172.60665,-43.60264],[172.60855,-43.60466],[172.60844,-43.60515],[172.60982,-43.60600],[172.61121,-43.60618],[172.61047,-43.60368],[172.61218,-43.60349],[172.61001,-43.60273],[172.61079,-43.60230],[172.61191,-43.60294],[172.61420,-43.60116],[172.61494,-43.60147],[172.61798,-43.59947],[172.61921,-43.59974],[172.62244,-43.59915],[172.62393,-43.60035],[172.62358,-43.60087],[172.62545,-43.60294],[172.62985,-43.60295],[172.63050,-43.60151],[172.63652,-43.60387],[172.63774,-43.60489],[172.63776,-43.60571],[172.63641,-43.60709],[172.63476,-43.60670],[172.63485,-43.60941],[172.63563,-43.60967],[172.63670,-43.60906],[172.63957,-43.60992],[172.63668,-43.61210],[172.63523,-43.61228],[172.63466,-43.61155],[172.63531,-43.61042],[172.63413,-43.60965],[172.63349,-43.61021],[172.63385,-43.61073],[172.63183,-43.61032],[172.62732,-43.61071],[172.62778,-43.61144],[172.62691,-43.61119],[172.62889,-43.61307],[172.62861,-43.61383],[172.62682,-43.61214],[172.62402,-43.61144],[172.62075,-43.60950],[172.62049,-43.61034],[172.61881,-43.61032],[172.62013,-43.60924],[172.61946,-43.60894],[172.61893,-43.60963],[172.61825,-43.60948],[172.61825,-43.60837],[172.61729,-43.60873],[172.61578,-43.60716],[172.61514,-43.60710],[172.61410,-43.60803],[172.62064,-43.61339],[172.62257,-43.61640],[172.62178,-43.61724],[172.62221,-43.61801],[172.62192,-43.61823],[172.62394,-43.61953],[172.62463,-43.61944],[172.62457,-43.61992],[172.62534,-43.62044],[172.62719,-43.61983],[172.63010,-43.62138],[172.63040,-43.62245],[172.63198,-43.62404],[172.63037,-43.62425],[172.62845,-43.62382],[172.62866,-43.62441],[172.62784,-43.62437],[172.62761,-43.62491],[172.62744,-43.62443],[172.62648,-43.62665],[172.62738,-43.62670],[172.62711,-43.62524],[172.62767,-43.62572],[172.62941,-43.62586],[172.62950,-43.62644],[172.62869,-43.62614],[172.62954,-43.62704],[172.63124,-43.62735],[172.63165,-43.62768],[172.63106,-43.62804],[172.63331,-43.62925],[172.63358,-43.63055],[172.63423,-43.63059],[172.63376,-43.63127],[172.63210,-43.63070],[172.63228,-43.63158],[172.63149,-43.63166],[172.62931,-43.62981],[172.62854,-43.62789],[172.62644,-43.62749],[172.62455,-43.62597],[172.62257,-43.62555],[172.62112,-43.62341],[172.61866,-43.62418],[172.61593,-43.62584],[172.61518,-43.62494],[172.61139,-43.62482],[172.60973,-43.62583],[172.60812,-43.62461],[172.60901,-43.62383],[172.60687,-43.62291],[172.60542,-43.62387],[172.60485,-43.62299],[172.60656,-43.62251],[172.60744,-43.62103],[172.60428,-43.61764]]
array_2024 = arcpy.Array([arcpy.Point(x, y) for x, y in COORDS_2024])
poly = arcpy.Polygon(array_2024, wgs84).projectAs(nztm)
arcpy.management.CopyFeatures(poly, "in_memory/aoi2024")

lcdb_path = r"J:\Data\Landcover_Database_v6\lcdb-v60-land-cover-database-version-60-mainland-new-zealand.shp"
lcdb_clip = "in_memory/lcdb_clip"
arcpy.analysis.Clip(lcdb_path, "in_memory/aoi2024", lcdb_clip)

# 2023-epoch pine-legacy footprint (consistent with the other 3 classes)
pine_lyr = arcpy.management.MakeFeatureLayer(lcdb_clip, "pine2023_lyr",
    where_clause="Name_2023 IN ('Exotic Forest', 'Forest - Harvested')")
pine_2023_fc = "in_memory/pine_2023"
arcpy.management.Dissolve(pine_lyr, pine_2023_fc)
pine_2023_ha = sum(r[0] for r in arcpy.da.SearchCursor(pine_2023_fc, ["SHAPE@AREA"])) / 10000.0
print(f"2023-epoch pine-legacy footprint (Exotic Forest + Forest-Harvested): {pine_2023_ha:.1f} ha")

geojson_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\hansen_loss_2017_2023.geojson"
with open(geojson_path) as f:
    gj = json.load(f)
hansen_fc = "in_memory/hansen_loss"
arcpy.management.CreateFeatureclass("in_memory", "hansen_loss", "POLYGON", spatial_reference=wgs84)
with arcpy.da.InsertCursor(hansen_fc, ["SHAPE@"]) as cur:
    for feat in gj["features"]:
        geom = feat["geometry"]
        if geom["type"] != "Polygon":
            continue
        array = arcpy.Array()
        for ring in geom["coordinates"]:
            array.add(arcpy.Array([arcpy.Point(x, y) for x, y in ring]))
        cur.insertRow([arcpy.Polygon(array, wgs84)])
hansen_nztm = "in_memory/hansen_nztm"
arcpy.management.Project(hansen_fc, hansen_nztm, nztm)
hansen_dissolved = "in_memory/hansen_dissolved"
arcpy.management.Dissolve(hansen_nztm, hansen_dissolved)

out_dir = r"C:\Users\zhouy3d\Desktop\a3\2024_materials"
cleared_pine_fc = f"{out_dir}\\cleared_pine_2024.shp"
arcpy.analysis.Intersect([pine_2023_fc, hansen_dissolved], "in_memory/cp_multi")
arcpy.management.Dissolve("in_memory/cp_multi", cleared_pine_fc, multi_part="SINGLE_PART")
cleared_ha = sum(r[0] for r in arcpy.da.SearchCursor(cleared_pine_fc, ["SHAPE@AREA"])) / 10000.0
n_blocks = int(arcpy.management.GetCount(cleared_pine_fc)[0])
print(f"cleared_pine (2023 pine-legacy AND Hansen loss): {cleared_ha:.1f} ha, {n_blocks} parts")

exotic_pine_fc = f"{out_dir}\\exotic_pine_2024.shp"
arcpy.analysis.Erase(pine_2023_fc, cleared_pine_fc, exotic_pine_fc)
exotic_ha = sum(r[0] for r in arcpy.da.SearchCursor(exotic_pine_fc, ["SHAPE@AREA"])) / 10000.0
print(f"exotic_pine (2023 pine-legacy MINUS cleared_pine): {exotic_ha:.1f} ha")

# ---- final totals check across ALL 5 classes, all now on the 2023 epoch ----
areas = {"cleared_pine": cleared_ha, "exotic_pine": exotic_ha}
for cls, names in {
    "gorse_broom":     ["Gorse and/or Broom", "Manuka and/or Kanuka"],
    "pasture":         ["High Producing Exotic Grassland", "Low Producing Grassland"],
    "broadleaf_scrub": ["Broadleaved Indigenous Hardwoods"],
}.items():
    fc = f"{out_dir}\\{cls}_2024.shp"
    areas[cls] = sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / 10000.0

total = sum(areas.values())
print("\n=== Final 2024 class areas (5-class scheme, consistent 2023 epoch) ===")
for cls, ha in sorted(areas.items(), key=lambda x: -x[1]):
    print(f"  {cls:18s} {ha:7.1f} ha  ({100*ha/total:4.1f}%)")
print(f"  {'TOTAL classified':18s} {total:7.1f} ha  (AOI = 467.3 ha, diff = {total-467.3:+.1f} ha)")
