"""
Intuitive before/after of pre-fire logging.
Left  = 2016 summer true colour (before: still forest)
Right = 2017 pre-fire true colour (after), with 2016 Hansen forest-loss painted RED.
-> real satellite view + red = "these trees were cut before the fire".
Output: A3/harvest_check/harvest_before_after.png  (auto-opens)
"""
import ee, urllib.request
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
OUT = "/Users/sodawaitress/Desktop/ERST619/A3/harvest_check/harvest_before_after.png"

def l8_truecolor(start, end):
    def prep(img):
        qa = img.select('QA_PIXEL')
        cloud = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
        return img.select('SR_B.').multiply(0.0000275).add(-0.2).updateMask(cloud.Not())
    med = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(AOI).filterDate(start, end).map(prep).median())
    return med.select(['SR_B4', 'SR_B3', 'SR_B2']).visualize(min=0, max=0.30)

before = l8_truecolor('2016-01-01', '2016-03-31')          # summer 2016
after_rgb = l8_truecolor('2016-11-01', '2017-02-12')       # 2017 pre-fire

# 2016 forest loss -> red overlay on the "after" image
loss16 = ee.Image('UMD/hansen/global_forest_change_2023_v1_11').select('lossyear').eq(16)
loss_red = loss16.selfMask().visualize(palette=['ff0000'])
after = after_rgb.blend(loss_red)

def fetch(img, path):
    url = img.getThumbURL({'region': AOI, 'dimensions': 700, 'format': 'png'})
    urllib.request.urlretrieve(url, path)

fetch(before, "/tmp/before.png")
fetch(after,  "/tmp/after.png")

fig, ax = plt.subplots(1, 2, figsize=(14, 7))
ax[0].imshow(mpimg.imread("/tmp/before.png")); ax[0].set_title("2016 (before harvest)"); ax[0].axis("off")
ax[1].imshow(mpimg.imread("/tmp/after.png"));  ax[1].set_title("2017 pre-fire (after) - RED = logged"); ax[1].axis("off")
plt.tight_layout(); plt.savefig(OUT, dpi=140)
print("saved ->", OUT)
