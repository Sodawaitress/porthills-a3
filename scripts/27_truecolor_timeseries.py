"""
27 — natural-colour (human-eye) time series for the whole fire story.
Everything is plain RGB true colour so a non-specialist can just SEE it:
green hills -> smoke on ignition day -> black scar -> green again a year on.
No false colour, no indices — the eye does the work.

Run on the GEE-authenticated machine: python 27_truecolor_timeseries.py
Author: Claude (for Yu Zhou), 2026-09-21
"""
import ee, io, urllib.request
from PIL import Image

ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])   # same frame as the 2/13 & 2/23 scenes
DIM = 1000
OUT = "/Users/sodawaitress/Desktop/ERST619/A3/website/assets/"


def save(img, vis, name):
    url = img.getThumbURL({'region': AOI, 'dimensions': DIM, 'format': 'png', **vis})
    Image.open(io.BytesIO(urllib.request.urlopen(url).read())).save(OUT + name)
    print("wrote", name)


# BEFORE — Sentinel-2 L1C (no L2A pre-fire scene exists here), least-cloud early-Feb view
pre = ee.Image(ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
               .filterBounds(AOI).filterDate('2017-01-20', '2017-02-12')
               .sort('CLOUDY_PIXEL_PERCENTAGE').first())
print("pre scene:", ee.Date(pre.get('system:time_start')).format('YYYY-MM-dd').getInfo())
save(pre.select(['B4', 'B3', 'B2']).divide(10000), {'min': 0, 'max': 0.3}, 'fire_pre_truecolour.png')

# RECOVERY — one year on, Sentinel-2 L2A, least cloud
rec = ee.Image(ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
               .filterBounds(AOI).filterDate('2018-02-01', '2018-03-20')
               .sort('CLOUDY_PIXEL_PERCENTAGE').first())
print("recovery scene:", ee.Date(rec.get('system:time_start')).format('YYYY-MM-dd').getInfo())
save(rec.select(['B4', 'B3', 'B2']).divide(10000), {'min': 0, 'max': 0.3}, 'fire_recovery_truecolour.png')

print("done")
