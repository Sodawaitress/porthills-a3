"""
2024 Port Hills fire - find a data-driven CHM height threshold to split
"exotic_pine" (real canopy) from "cleared_pine" (disturbed/regrowth, no closed
canopy yet) within LCDB's Exotic Forest + Forest-Harvested footprint.

Not picking a round number by eye - fit a 2-component split (k-means, k=2) on the
CHM values inside that footprint, and also show the histogram so the split can be
sanity-checked visually.

Author: Claude (for Yu Zhou), 2026-09-20
"""
import arcpy
import numpy as np
import matplotlib.pyplot as plt

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

nztm = arcpy.SpatialReference(2193)
wgs84 = arcpy.SpatialReference(4326)
aoi_fc = "in_memory/aoi_2024"
COORDS_2024 = [[172.60428,-43.61764],[172.60529,-43.61721],[172.60505,-43.61653],[172.60564,-43.61569],[172.60610,-43.61558],[172.60807,-43.61769],[172.61197,-43.61568],[172.61070,-43.61552],[172.60941,-43.61457],[172.60867,-43.61489],[172.60668,-43.61380],[172.60871,-43.61330],[172.60692,-43.61304],[172.60518,-43.61099],[172.60693,-43.60866],[172.60713,-43.60674],[172.60642,-43.60636],[172.60708,-43.60469],[172.60665,-43.60264],[172.60855,-43.60466],[172.60844,-43.60515],[172.60982,-43.60600],[172.61121,-43.60618],[172.61047,-43.60368],[172.61218,-43.60349],[172.61001,-43.60273],[172.61079,-43.60230],[172.61191,-43.60294],[172.61420,-43.60116],[172.61494,-43.60147],[172.61798,-43.59947],[172.61921,-43.59974],[172.62244,-43.59915],[172.62393,-43.60035],[172.62358,-43.60087],[172.62545,-43.60294],[172.62985,-43.60295],[172.63050,-43.60151],[172.63652,-43.60387],[172.63774,-43.60489],[172.63776,-43.60571],[172.63641,-43.60709],[172.63476,-43.60670],[172.63485,-43.60941],[172.63563,-43.60967],[172.63670,-43.60906],[172.63957,-43.60992],[172.63668,-43.61210],[172.63523,-43.61228],[172.63466,-43.61155],[172.63531,-43.61042],[172.63413,-43.60965],[172.63349,-43.61021],[172.63385,-43.61073],[172.63183,-43.61032],[172.62732,-43.61071],[172.62778,-43.61144],[172.62691,-43.61119],[172.62889,-43.61307],[172.62861,-43.61383],[172.62682,-43.61214],[172.62402,-43.61144],[172.62075,-43.60950],[172.62049,-43.61034],[172.61881,-43.61032],[172.62013,-43.60924],[172.61946,-43.60894],[172.61893,-43.60963],[172.61825,-43.60948],[172.61825,-43.60837],[172.61729,-43.60873],[172.61578,-43.60716],[172.61514,-43.60710],[172.61410,-43.60803],[172.62064,-43.61339],[172.62257,-43.61640],[172.62178,-43.61724],[172.62221,-43.61801],[172.62192,-43.61823],[172.62394,-43.61953],[172.62463,-43.61944],[172.62457,-43.61992],[172.62534,-43.62044],[172.62719,-43.61983],[172.63010,-43.62138],[172.63040,-43.62245],[172.63198,-43.62404],[172.63037,-43.62425],[172.62845,-43.62382],[172.62866,-43.62441],[172.62784,-43.62437],[172.62761,-43.62491],[172.62744,-43.62443],[172.62648,-43.62665],[172.62738,-43.62670],[172.62711,-43.62524],[172.62767,-43.62572],[172.62941,-43.62586],[172.62950,-43.62644],[172.62869,-43.62614],[172.62954,-43.62704],[172.63124,-43.62735],[172.63165,-43.62768],[172.63106,-43.62804],[172.63331,-43.62925],[172.63358,-43.63055],[172.63423,-43.63059],[172.63376,-43.63127],[172.63210,-43.63070],[172.63228,-43.63158],[172.63149,-43.63166],[172.62931,-43.62981],[172.62854,-43.62789],[172.62644,-43.62749],[172.62455,-43.62597],[172.62257,-43.62555],[172.62112,-43.62341],[172.61866,-43.62418],[172.61593,-43.62584],[172.61518,-43.62494],[172.61139,-43.62482],[172.60973,-43.62583],[172.60812,-43.62461],[172.60901,-43.62383],[172.60687,-43.62291],[172.60542,-43.62387],[172.60485,-43.62299],[172.60656,-43.62251],[172.60744,-43.62103],[172.60428,-43.61764]]
array_2024 = arcpy.Array([arcpy.Point(x, y) for x, y in COORDS_2024])
poly_2024_nztm = arcpy.Polygon(array_2024, wgs84).projectAs(nztm)
arcpy.management.CopyFeatures(poly_2024_nztm, aoi_fc)

lcdb_path = r"J:\Data\Landcover_Database_v6\lcdb-v60-land-cover-database-version-60-mainland-new-zealand.shp"
lcdb_clip = "in_memory/lcdb_clip3"
arcpy.analysis.Clip(lcdb_path, aoi_fc, lcdb_clip)

lyr = arcpy.management.MakeFeatureLayer(lcdb_clip, "pine_lyr",
    where_clause="Name_2023 IN ('Exotic Forest', 'Forest - Harvested')")
pine_fc = "in_memory/pine_footprint"
arcpy.management.Dissolve(lyr, pine_fc)

chm_capped_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_2024_AOI_capped.tif"
chm_pine = arcpy.sa.ExtractByMask(chm_capped_path, pine_fc)
arr = arcpy.RasterToNumPyArray(chm_pine, nodata_to_value=np.nan)
vals = arr[~np.isnan(arr)]
print("Pixels in Exotic Forest + Forest-Harvested footprint:", vals.size,
      "= %.1f ha" % (vals.size / 10000.0))
print("percentiles 10/25/50/75/90:", np.percentile(vals, [10, 25, 50, 75, 90]))

# k-means k=2 (no sklearn dependency assumed available here - do it by hand, 1D)
def kmeans_1d(x, k=2, n_iter=50, seed=0):
    rng = np.random.default_rng(seed)
    centers = rng.choice(x, size=k, replace=False)
    for _ in range(n_iter):
        dists = np.abs(x[:, None] - centers[None, :])
        assign = np.argmin(dists, axis=1)
        new_centers = np.array([x[assign == i].mean() if np.any(assign == i) else centers[i] for i in range(k)])
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return centers, assign

sample = vals if vals.size < 200000 else np.random.default_rng(0).choice(vals, 200000, replace=False)
centers, assign = kmeans_1d(sample, k=2)
centers_sorted = np.sort(centers)
threshold = centers_sorted.mean()  # midpoint between the two cluster centers
print("k-means centers:", centers_sorted, "-> midpoint threshold candidate: %.2f m" % threshold)

frac_above = np.mean(vals >= threshold)
print(f"Fraction of Exotic Forest+Forest-Harvested area with CHM >= {threshold:.2f}m "
      f"(would become exotic_pine): {100*frac_above:.1f}%")
print(f"Fraction < threshold (cleared_pine): {100*(1-frac_above):.1f}%")

plt.figure(figsize=(8, 5))
plt.hist(vals, bins=80, color="steelblue", edgecolor="none")
plt.axvline(threshold, color="red", linestyle="--", label=f"k-means midpoint = {threshold:.2f}m")
plt.xlabel("Canopy height (m), capped 0-40m")
plt.ylabel("pixel count (1m cells)")
plt.title("CHM distribution inside LCDB 'Exotic Forest' + 'Forest - Harvested'\n(2024 fire AOI)")
plt.legend()
plt.tight_layout()
out_png = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_histogram_pine_threshold.png"
plt.savefig(out_png, dpi=150)
print("Saved:", out_png)
