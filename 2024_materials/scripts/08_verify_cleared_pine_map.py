"""Quick visual check: cleared_pine (188.9ha) vs exotic_pine (36.7ha) polygons,
over the CHM backdrop, for the 2024 fire AOI. Same spirit as 2017's
harvest_check/cleared_pine_blocks.png sanity check."""
import arcpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

chm_capped_path = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\CHM_2024_AOI_capped.tif"
chm_ras = arcpy.Raster(chm_capped_path)
extent = chm_ras.extent
arr = arcpy.RasterToNumPyArray(chm_ras, nodata_to_value=np.nan)

def polys_from_shp(path):
    parts = []
    with arcpy.da.SearchCursor(path, ["SHAPE@"]) as cur:
        for (shape,) in cur:
            for part in shape:
                ring = [(pt.X, pt.Y) for pt in part if pt is not None]
                if len(ring) >= 3:
                    parts.append(ring)
    return parts

cleared_polys = polys_from_shp(r"C:\Users\zhouy3d\Desktop\a3\2024_materials\cleared_pine_2024.shp")
exotic_polys = polys_from_shp(r"C:\Users\zhouy3d\Desktop\a3\2024_materials\exotic_pine_2024.shp")

fig, ax = plt.subplots(figsize=(9, 9))
ax.imshow(arr, cmap="Greys", vmin=0, vmax=8,
          extent=[extent.XMin, extent.XMax, extent.YMin, extent.YMax], origin="upper")

cleared_patches = [MplPolygon(p, closed=True) for p in cleared_polys]
exotic_patches = [MplPolygon(p, closed=True) for p in exotic_polys]
ax.add_collection(PatchCollection(cleared_patches, facecolor="orangered", alpha=0.5,
                                   edgecolor="orangered", linewidth=0.5, label="cleared_pine (188.9 ha)"))
ax.add_collection(PatchCollection(exotic_patches, facecolor="darkgreen", alpha=0.6,
                                   edgecolor="darkgreen", linewidth=0.5, label="exotic_pine (36.7 ha)"))

ax.set_xlim(extent.XMin, extent.XMax)
ax.set_ylim(extent.YMin, extent.YMax)
ax.set_aspect("equal")
ax.set_title("2024 fire AOI: pre-fire pine footprint split\ncleared_pine (Hansen loss 2017-2023) vs exotic_pine (rest)\nbackdrop = CHM (grey, 0-8m)")
ax.legend(loc="lower left", fontsize=9)
ax.axis("off")

out_png = r"C:\Users\zhouy3d\Desktop\a3\2024_materials\figures\cleared_pine_vs_exotic_pine_2024.png"
plt.tight_layout()
plt.savefig(out_png, dpi=150)
print("Saved:", out_png)
