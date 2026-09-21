"""
Export A1's visualisation panels as static PNGs - LOCAL version, no GEE.

Corrected after the other machine pointed out the obvious: A1 already
exported PortHills2017_stack.tif (22 bands) to
C:\\Users\\zhouy3d\\Desktop\\PortHills\\data\\PortHills2017_stack.tif, and
the rest of the 2017 pipeline already reads this file locally via arcpy.
Re-deriving everything from GEE in Python (the first version of this
script) was needless.

Band order (from 00_A1_PortHills_dNBR.js's export comment, 1-indexed):
1-6 pre_B2..B7, 7-12 post_B2..B7, 13 NBR_pre, 14 NBR_post, 15 dNBR,
16 NDVI, 17 BSI, 18 severity, 19 valid_data, 20 elev, 21 slope, 22 northness

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy
import numpy as np
import matplotlib.pyplot as plt
import os

STACK = r"C:\Users\zhouy3d\Desktop\PortHills\data\PortHills2017_stack.tif"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"
os.makedirs(OUT_DIR, exist_ok=True)

arr = arcpy.RasterToNumPyArray(STACK, nodata_to_value=np.nan)  # (22, rows, cols)


def b(n):
    """1-indexed band -> 2D array."""
    return arr[n - 1]


def stretch_rgb(idx_1based):
    chans = []
    for n in idx_1based:
        a = b(n)
        lo, hi = np.nanpercentile(a, [2, 98])
        chans.append(np.clip((a - lo) / (hi - lo + 1e-9), 0, 1))
    return np.dstack(chans)


panels = {
    "natural_colour_pre":  [3, 2, 1],     # pre_B4,B3,B2
    "natural_colour_post": [9, 8, 7],     # post_B4,B3,B2
    "cir_pre":             [4, 3, 2],     # pre_B5,B4,B3
    "burn_swir_post":      [12, 10, 9],   # post_B7,B5,B4
}

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
for ax, (name, idx) in zip(axes.flat, panels.items()):
    ax.imshow(stretch_rgb(idx))
    ax.set_title(name)
    ax.axis("off")

im = axes.flat[4].imshow(b(16), cmap="RdYlGn", vmin=-0.2, vmax=0.8)
axes.flat[4].set_title("NDVI (pre-fire)")
axes.flat[4].axis("off")
plt.colorbar(im, ax=axes.flat[4], fraction=0.046)

im2 = axes.flat[5].imshow(b(15), cmap="RdYlBu_r", vmin=-200, vmax=800)
axes.flat[5].set_title("dNBR (raw, A1 stack)")
axes.flat[5].axis("off")
plt.colorbar(im2, ax=axes.flat[5], fraction=0.046)

plt.tight_layout()
out1 = os.path.join(OUT_DIR, "A1_visualisation_panels.png")
plt.savefig(out1, dpi=120)
print("Wrote", out1)

fig2, ax2 = plt.subplots(figsize=(8, 7))
im3 = ax2.imshow(b(17), cmap="YlOrBr", vmin=-0.5, vmax=0.5)
ax2.set_title("BSI (Bare Soil Index, pre-fire)")
ax2.axis("off")
plt.colorbar(im3, ax=ax2, fraction=0.046)
out_bsi = os.path.join(OUT_DIR, "A1_bsi.png")
plt.savefig(out_bsi, dpi=120)
print("Wrote", out_bsi)

print("\nNOTE: the true-colour + shadow-frequency figure (how often each "
      "scene gets flagged shadow) still needs the raw per-scene Landsat "
      "collection, not this composited stack - that part still needs GEE, "
      "see the bottom half of the previous version of this script / adapt "
      "2024's 23_truecolor_burn_vs_cloud.py with QA_PIXEL bit4.")
