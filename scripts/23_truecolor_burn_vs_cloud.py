"""
Visual proof: are the pixels SCL masks as "cloud shadow" (class 3) actually
CLOUD, or BURN SCARS? Pick the least-cloudy post-fire S2 scene, show it in true
colour (burns = dark, cloud = white), and paint where SCL==3 in red. If the red
sits on the dark burn scars, SCL is mislabelling burns as shadow (the cause of
the 126/243 gap in 22 before the fix).

Output: exploration/truecolor_burn_vs_cloud.png (2 panels + training points).

Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee
import os
import csv
import io
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

ee.Initialize(project='genuine-hold-427410-f0')
HERE = os.path.dirname(os.path.abspath(__file__))
PTS = os.path.join(HERE, "..", "TrainingPoints_2024_wgs84.csv")
OUT = os.path.join(HERE, "..", "exploration", "truecolor_burn_vs_cloud.png")

W, S, E, N = 172.55, -43.65, 172.67, -43.56
AOI = ee.Geometry.Rectangle([W, S, E, N])

coll = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(AOI).filterDate('2024-02-20', '2024-03-31')
        .sort('CLOUDY_PIXEL_PERCENTAGE'))
scene = ee.Image(coll.first())
date = ee.Date(scene.get('system:time_start')).format('YYYY-MM-dd').getInfo()
cc = scene.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
print(f"Least-cloudy post-fire scene: {date}  (scene cloud {cc:.1f}%)")

DIM = 900


def fetch(img, vis):
    url = img.getThumbURL({'region': AOI, 'dimensions': DIM,
                           'format': 'png', **vis})
    return np.array(Image.open(io.BytesIO(urllib.request.urlopen(url).read())))


# true colour (reflectance 0-0.30) of the clean scene, and - the real proof -
# how OFTEN each pixel is flagged SCL==3 ("cloud shadow") across the whole
# post-fire window. A burn scar that keeps getting called "shadow" lights up.
tc = fetch(scene.select(['B4', 'B3', 'B2']).divide(10000),
           {'min': 0.0, 'max': 0.30})
scl3_freq = coll.map(lambda im: im.select('SCL').eq(3)).mean()
freq = fetch(scl3_freq, {'min': 0, 'max': 1,
                         'palette': ['000044', '0000ff', '00ffff',
                                     'ffff00', 'ff0000']})

pts = list(csv.DictReader(open(PTS)))
lon = [float(r['lon']) for r in pts]
lat = [float(r['lat']) for r in pts]

fig, ax = plt.subplots(1, 2, figsize=(15, 7))
for a in ax:
    a.set_xlim(W, E); a.set_ylim(S, N)
    a.scatter(lon, lat, s=8, facecolors='none', edgecolors='cyan', linewidths=0.5)
ax[0].imshow(tc, extent=[W, E, S, N])
ax[0].set_title(f"True colour, post-fire {date}\n(burn scars = dark, cloud = white)")
ax[1].imshow(freq, extent=[W, E, S, N])
ax[1].set_title('How often SCL calls each pixel "cloud shadow"\n'
                '(whole post-fire window; hot/red = repeatedly flagged)')
plt.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
plt.savefig(OUT, dpi=110, bbox_inches='tight')
print(f"Wrote {OUT}")
