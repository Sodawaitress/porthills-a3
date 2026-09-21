"""
2017 true-colour + "how often QA_PIXEL flags this pixel cloud shadow" figure
- the visual case for A1's smart mask (00_A1_PortHills_dNBR.js line 78-87:
  shadow flag restricted to outside the fire perimeter because it was
  removing 242ha of char that reads spectrally like shadow).

This is the 2017/Landsat equivalent of 2024's 23_truecolor_burn_vs_cloud.py
(which used Sentinel-2 SCL==3 - NOT the same thing, don't reuse that output
for 2017, they're different fires/sensors/years).

Needs the raw per-scene Landsat collection (frequency across scenes), which
isn't preserved in the already-exported composited PortHills2017_stack.tif -
this part genuinely needs GEE, unlike 24_A1_export_figures.py.

Run on the GEE-authenticated machine: python 25_2017_truecolor_shadow_freq.py

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import io
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

ee.Initialize(project='genuine-hold-427410-f0')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "exploration", "A1_truecolor_burn_vs_shadow_2017.png")

ASSET_ID = 'projects/genuine-hold-427410-f0/assets/Port_Hills_2017_Fire_Boundary'
raw = ee.FeatureCollection(ASSET_ID)
fireWithHoles = raw.filter(ee.Filter.eq('Type', 'Fire Boundary')).first().geometry()
unburntFC = raw.filter(ee.Filter.eq('Type', 'Unburnt'))
aoi = fireWithHoles.union(unburntFC.geometry(), 1)
mapFrame = aoi.buffer(500)

postStart, postEnd = '2017-02-24', '2017-03-30'  # same window as A1


def scaleSR(image):
    return (image.select('SR_B.').multiply(0.0000275).add(-0.2)
            .copyProperties(image, ['system:time_start']))


l8_post = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(mapFrame).filterDate(postStart, postEnd))

least_cloudy = l8_post.sort('CLOUD_COVER').first()
date = ee.Date(least_cloudy.get('system:time_start')).format('YYYY-MM-dd').getInfo()
cc = least_cloudy.get('CLOUD_COVER').getInfo()
print(f"Least-cloudy post-fire Landsat scene: {date} (scene cloud {cc:.1f}%)")

DIM = 900


def fetch(img, vis):
    url = img.getThumbURL({'region': mapFrame, 'dimensions': DIM, 'format': 'png', **vis})
    return np.array(Image.open(io.BytesIO(urllib.request.urlopen(url).read())))


tc_img = ee.Image(scaleSR(least_cloudy)).select(['SR_B4', 'SR_B3', 'SR_B2']).clip(mapFrame)
tc = fetch(tc_img, {'min': 0, 'max': 0.30})

# bit4 = cloud shadow in QA_PIXEL
shadow_freq = l8_post.map(
    lambda im: im.select('QA_PIXEL').bitwiseAnd(1 << 4).neq(0)
).mean().clip(mapFrame)
freq = fetch(shadow_freq, {'min': 0, 'max': 1,
                            'palette': ['000044', '0000ff', '00ffff', 'ffff00', 'ff0000']})

fig, ax = plt.subplots(1, 2, figsize=(15, 7))
ax[0].imshow(tc)
ax[0].set_title(f"2017 Port Hills, true colour, post-fire {date}\n(burn scar = dark, cloud = white)")
ax[0].axis("off")
ax[1].imshow(freq)
ax[1].set_title('How often QA_PIXEL bit4 flags each pixel "cloud shadow"\n'
                 '(whole post-fire window 2017-02-24 to 2017-03-30)\n'
                 'hot/red inside the fire perimeter = why the mask had to be restricted there')
ax[1].axis("off")
plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=110, bbox_inches='tight')
print("Wrote", OUT)
