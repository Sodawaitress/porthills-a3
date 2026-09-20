"""
2024 Port Hills fire - bare_rock candidate search, same method as 2017
(US1.6: slope > 60 deg, connected-component clusters, then check each by hand).
No aerial photo available for 2024 (checked, not worth chasing - see chat), so
this can only get to "candidate clusters + CHM cross-check", not the full
2017-style visual confirmation. Reporting that honestly rather than treating
these as confirmed bare-rock points.

Author: Claude (for Yu Zhou), 2026-09-20
"""
import arcpy
import numpy as np
from scipy import ndimage

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

wgs84 = arcpy.SpatialReference(4326)
nztm = arcpy.SpatialReference(2193)
COORDS_2024 = [[172.60428,-43.61764],[172.60529,-43.61721],[172.60505,-43.61653],[172.60564,-43.61569],[172.60610,-43.61558],[172.60807,-43.61769],[172.61197,-43.61568],[172.61070,-43.61552],[172.60941,-43.61457],[172.60867,-43.61489],[172.60668,-43.61380],[172.60871,-43.61330],[172.60692,-43.61304],[172.60518,-43.61099],[172.60693,-43.60866],[172.60713,-43.60674],[172.60642,-43.60636],[172.60708,-43.60469],[172.60665,-43.60264],[172.60855,-43.60466],[172.60844,-43.60515],[172.60982,-43.60600],[172.61121,-43.60618],[172.61047,-43.60368],[172.61218,-43.60349],[172.61001,-43.60273],[172.61079,-43.60230],[172.61191,-43.60294],[172.61420,-43.60116],[172.61494,-43.60147],[172.61798,-43.59947],[172.61921,-43.59974],[172.62244,-43.59915],[172.62393,-43.60035],[172.62358,-43.60087],[172.62545,-43.60294],[172.62985,-43.60295],[172.63050,-43.60151],[172.63652,-43.60387],[172.63774,-43.60489],[172.63776,-43.60571],[172.63641,-43.60709],[172.63476,-43.60670],[172.63485,-43.60941],[172.63563,-43.60967],[172.63670,-43.60906],[172.63957,-43.60992],[172.63668,-43.61210],[172.63523,-43.61228],[172.63466,-43.61155],[172.63531,-43.61042],[172.63413,-43.60965],[172.63349,-43.61021],[172.63385,-43.61073],[172.63183,-43.61032],[172.62732,-43.61071],[172.62778,-43.61144],[172.62691,-43.61119],[172.62889,-43.61307],[172.62861,-43.61383],[172.62682,-43.61214],[172.62402,-43.61144],[172.62075,-43.60950],[172.62049,-43.61034],[172.61881,-43.61032],[172.62013,-43.60924],[172.61946,-43.60894],[172.61893,-43.60963],[172.61825,-43.60948],[172.61825,-43.60837],[172.61729,-43.60873],[172.61578,-43.60716],[172.61514,-43.60710],[172.61410,-43.60803],[172.62064,-43.61339],[172.62257,-43.61640],[172.62178,-43.61724],[172.62221,-43.61801],[172.62192,-43.61823],[172.62394,-43.61953],[172.62463,-43.61944],[172.62457,-43.61992],[172.62534,-43.62044],[172.62719,-43.61983],[172.63010,-43.62138],[172.63040,-43.62245],[172.63198,-43.62404],[172.63037,-43.62425],[172.62845,-43.62382],[172.62866,-43.62441],[172.62784,-43.62437],[172.62761,-43.62491],[172.62744,-43.62443],[172.62648,-43.62665],[172.62738,-43.62670],[172.62711,-43.62524],[172.62767,-43.62572],[172.62941,-43.62586],[172.62950,-43.62644],[172.62869,-43.62614],[172.62954,-43.62704],[172.63124,-43.62735],[172.63165,-43.62768],[172.63106,-43.62804],[172.63331,-43.62925],[172.63358,-43.63055],[172.63423,-43.63059],[172.63376,-43.63127],[172.63210,-43.63070],[172.63228,-43.63158],[172.63149,-43.63166],[172.62931,-43.62981],[172.62854,-43.62789],[172.62644,-43.62749],[172.62455,-43.62597],[172.62257,-43.62555],[172.62112,-43.62341],[172.61866,-43.62418],[172.61593,-43.62584],[172.61518,-43.62494],[172.61139,-43.62482],[172.60973,-43.62583],[172.60812,-43.62461],[172.60901,-43.62383],[172.60687,-43.62291],[172.60542,-43.62387],[172.60485,-43.62299],[172.60656,-43.62251],[172.60744,-43.62103],[172.60428,-43.61764]]
array_2024 = arcpy.Array([arcpy.Point(x, y) for x, y in COORDS_2024])
poly = arcpy.Polygon(array_2024, wgs84).projectAs(nztm)
arcpy.management.CopyFeatures(poly, "in_memory/aoi2024")

dem = r"J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DEM.tif"
dem_clip = arcpy.sa.ExtractByMask(dem, "in_memory/aoi2024")
slope = arcpy.sa.Slope(dem_clip, "DEGREE")
slope_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\Slope_2024_AOI.tif"
slope.save(slope_path)

chm_capped_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_2024_AOI_capped.tif"
slope_ras = arcpy.Raster(slope_path)
extent = slope_ras.extent
cell = slope_ras.meanCellWidth

slope_arr = arcpy.RasterToNumPyArray(slope_ras, nodata_to_value=np.nan)
chm_arr = arcpy.RasterToNumPyArray(chm_capped_path, nodata_to_value=np.nan)
# CHM and slope grids may differ by a row/col from independent ExtractByMask calls; crop to common shape
h = min(slope_arr.shape[0], chm_arr.shape[0]); w = min(slope_arr.shape[1], chm_arr.shape[1])
slope_arr = slope_arr[:h, :w]; chm_arr = chm_arr[:h, :w]

mask = slope_arr > 60
labels, n = ndimage.label(mask)
print(f"Found {n} connected clusters at slope > 60 deg")

results = []
for i in range(1, n + 1):
    ys, xs = np.where(labels == i)
    npix = len(ys)
    if npix < 4:   # drop single/double-pixel speckle, same spirit as 2017's MIN_PIX filtering
        continue
    cy, cx = ys.mean(), xs.mean()
    # convert array row/col -> map coords (row 0 = top = YMax)
    map_x = extent.XMin + (cx + 0.5) * cell
    map_y = extent.YMax - (cy + 0.5) * cell
    chm_vals = chm_arr[ys, xs]
    chm_median = np.nanmedian(chm_vals)
    # shape check: linear features (DEM seams / tracks) have high bbox aspect ratio
    # and low fill ratio; blobby real outcrops are closer to square/round
    h_extent = ys.max() - ys.min() + 1
    w_extent = xs.max() - xs.min() + 1
    bbox_area = h_extent * w_extent
    fill_ratio = npix / bbox_area
    aspect = max(h_extent, w_extent) / max(1, min(h_extent, w_extent))
    results.append((i, npix, npix * cell * cell / 10000, map_x, map_y, chm_median, aspect, fill_ratio))

results.sort(key=lambda r: -r[1])
print(f"\n{len(results)} clusters with >=4 pixels:")
print(f"{'id':>3} {'pix':>5} {'ha':>6} {'NZTM_X':>10} {'NZTM_Y':>10} {'CHM_med':>8} {'aspect':>7} {'fill':>5}  guess")
for r in results:
    i, npix, ha, mx, my, chm_med, aspect, fill = r
    # heuristic: real rock outcrop = blobby (low aspect, higher fill) + near-zero CHM
    # DEM-seam/track artifact = very linear (high aspect, low fill)
    guess = "likely_artifact(linear)" if aspect > 4 and fill < 0.35 else "candidate_real"
    print(f"{i:3d} {npix:5d} {ha:6.3f} {mx:10.1f} {my:10.1f} {chm_med:8.2f} {aspect:7.1f} {fill:5.2f}  {guess}")

print("\nTotal slope>60 area (all clusters incl. <4px speckle):",
      f"{np.sum(mask)*cell*cell/10000:.2f} ha")
print("NOTE: no aerial photo available for 2024 to visually confirm these -")
print("the aspect/fill-ratio heuristic is a proxy, not a substitute for the")
print("2017 project's actual photo-interpretation pass. Report as candidates only.")
