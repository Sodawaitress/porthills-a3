"""
Port of A1's PortHills_dNBR (00_A1_PortHills_dNBR.js) to Python, purely to
EXPORT the visualisation layers as static PNGs for report.md - A1's own
logic is not changed, just re-run in Python so getThumbURL can save files
(the JS Code Editor only shows layers on screen, doesn't save them).

Also builds the 2017 equivalent of 2024's 23_truecolor_burn_vs_cloud.py:
true colour + "how often does QA_PIXEL flag this pixel as cloud shadow"
frequency map, side by side - the visual case for why bit4 (shadow) had to
be restricted to outside the fire perimeter.

Run on the GEE-authenticated machine: python 24_A1_export_figures.py

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import io
import csv
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

ee.Initialize(project='genuine-hold-427410-f0')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "exploration")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- 1. AOI (same asset A1 used) ----
ASSET_ID = 'projects/genuine-hold-427410-f0/assets/Port_Hills_2017_Fire_Boundary'
raw = ee.FeatureCollection(ASSET_ID)
fireWithHoles = raw.filter(ee.Filter.eq('Type', 'Fire Boundary')).first().geometry()
unburntFC = raw.filter(ee.Filter.eq('Type', 'Unburnt'))
aoi = fireWithHoles.union(unburntFC.geometry(), 1)
wideFrame = aoi.buffer(4000)
mapFrame = aoi.buffer(500)

preStart, preEnd = '2016-12-01', '2017-02-11'
postStart, postEnd = '2017-02-24', '2017-03-30'
outputBands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']


def scaleSR(image):
    return (image.select('SR_B.').multiply(0.0000275).add(-0.2)
            .copyProperties(image, ['system:time_start']))


def maskL8clouds_QA(image):
    qa = image.select('QA_PIXEL')
    inFire = ee.Image.constant(1).clip(aoi).mask()
    bad = (qa.bitwiseAnd(1 << 3).neq(0)
           .Or(qa.bitwiseAnd(1 << 4).neq(0).And(inFire.Not())))
    return ee.Image(scaleSR(image)).updateMask(bad.Not())


l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(wideFrame)
preCol = l8.filterDate(preStart, preEnd).map(maskL8clouds_QA)
postCol = l8.filterDate(postStart, postEnd).map(maskL8clouds_QA)
pre = preCol.select(outputBands).median().clip(mapFrame)
post = postCol.select(outputBands).median().clip(mapFrame)

ndviPre = pre.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
bsi = pre.expression(
    '((RED + SWIR) - (NIR + BLUE)) / ((RED + SWIR) + (NIR + BLUE))',
    {'RED': pre.select('SR_B4'), 'SWIR': pre.select('SR_B6'),
     'NIR': pre.select('SR_B5'), 'BLUE': pre.select('SR_B2')}).rename('BSI')

nbrPre = pre.normalizedDifference(['SR_B5', 'SR_B7'])
nbrPost = post.normalizedDifference(['SR_B5', 'SR_B7'])
dnbrRaw = nbrPre.subtract(nbrPost).multiply(1000)
# NOTE: this script exports figures only, it does NOT re-derive the offset/
# threshold (those need the full AOI-wide reduceRegion the JS version does,
# not worth duplicating here) - dnbrRaw (uncorrected) is fine for a visual.

DIM = 900


def fetch(img, vis):
    url = img.getThumbURL({'region': mapFrame, 'dimensions': DIM, 'format': 'png', **vis})
    return np.array(Image.open(io.BytesIO(urllib.request.urlopen(url).read())))


print("Fetching A1 visualisation layers...")
panels = {
    "1_natural_colour_pre": (pre, {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 0.3}),
    "2_natural_colour_post": (post, {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 0.3}),
    "3_cir_pre": (pre, {'bands': ['SR_B5', 'SR_B4', 'SR_B3'], 'min': 0, 'max': 0.4}),
    "4_burn_swir_post": (post, {'bands': ['SR_B7', 'SR_B5', 'SR_B4'], 'min': 0, 'max': 0.4}),
    "5_ndvi_pre": (ndviPre, {'min': -0.2, 'max': 0.8,
                              'palette': ['blue', 'white', 'yellow', 'green', 'darkgreen']}),
    "6_bsi": (bsi, {'min': -0.5, 'max': 0.5,
                     'palette': ['darkgreen', 'yellow', 'orange', 'brown', 'white']}),
    "7_dnbr_raw": (dnbrRaw, {'min': -200, 'max': 800,
                              'palette': ['2c7bb6', 'ffffbf', 'd7191c']}),
}

fig, axes = plt.subplots(3, 3, figsize=(18, 16))
for ax, (name, (img, vis)) in zip(axes.flat, panels.items()):
    arr = fetch(img, vis)
    ax.imshow(arr)
    ax.set_title(name)
    ax.axis("off")
for ax in axes.flat[len(panels):]:
    ax.axis("off")
plt.tight_layout()
out1 = os.path.join(OUT_DIR, "A1_visualisation_panels.png")
plt.savefig(out1, dpi=110)
print("Wrote", out1)

# ---- 2. true-colour + "how often is this pixel flagged shadow" frequency ----
# 2017 equivalent of 2024's 23_truecolor_burn_vs_cloud.py, using QA_PIXEL
# bit4 instead of Sentinel-2 SCL==3
post_scenes = l8.filterDate(postStart, postEnd)
least_cloudy = post_scenes.sort('CLOUD_COVER').first()
date = ee.Date(least_cloudy.get('system:time_start')).format('YYYY-MM-dd').getInfo()
cc = least_cloudy.get('CLOUD_COVER').getInfo()
print(f"Least-cloudy post-fire Landsat scene: {date} (scene cloud {cc:.1f}%)")

tc_img = ee.Image(scaleSR(least_cloudy)).select(['SR_B4', 'SR_B3', 'SR_B2']).clip(mapFrame)
tc = fetch(tc_img, {'min': 0, 'max': 0.30})

shadow_freq = post_scenes.map(
    lambda im: im.select('QA_PIXEL').bitwiseAnd(1 << 4).neq(0)
).mean().clip(mapFrame)
freq = fetch(shadow_freq, {'min': 0, 'max': 1,
                            'palette': ['000044', '0000ff', '00ffff', 'ffff00', 'ff0000']})

fig, ax = plt.subplots(1, 2, figsize=(15, 7))
ax[0].imshow(tc)
ax[0].set_title(f"True colour, post-fire {date}\n(burn scars = dark, cloud = white)")
ax[0].axis("off")
ax[1].imshow(freq)
ax[1].set_title('How often QA_PIXEL bit4 calls each pixel "cloud shadow"\n'
                 '(whole post-fire window; hot/red = repeatedly flagged)\n'
                 'fire perimeter outline should sit on the hot zone if the fix is justified')
ax[1].axis("off")
plt.tight_layout()
out2 = os.path.join(OUT_DIR, "A1_truecolor_burn_vs_shadow_2017.png")
plt.savefig(out2, dpi=110)
print("Wrote", out2)
