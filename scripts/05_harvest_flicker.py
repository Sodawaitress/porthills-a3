"""
Blink-comparison animation: 2016 <-> 2017 pre-fire true colour (no overlay).
Unchanged ground stays still; logged/changed patches "flicker" -> you spot
them yourself on the real imagery, nothing hidden.
Output: A3/harvest_check/harvest_flicker.gif
"""
import ee, urllib.request
from PIL import Image, ImageDraw, ImageFont
ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
GIF = "/Users/sodawaitress/Desktop/ERST619/A3/harvest_check/harvest_flicker.gif"
DIM = 900

def l8_truecolor(start, end):
    def prep(img):
        qa = img.select('QA_PIXEL')
        cloud = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1 << 4))
        return img.select('SR_B.').multiply(0.0000275).add(-0.2).updateMask(cloud.Not())
    med = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(AOI).filterDate(start, end).map(prep).median())
    return med.select(['SR_B4', 'SR_B3', 'SR_B2']).visualize(min=0, max=0.30)

def fetch(img, path):
    url = img.getThumbURL({'region': AOI, 'dimensions': DIM, 'format': 'png'})
    urllib.request.urlretrieve(url, path)

fetch(l8_truecolor('2016-01-01', '2016-03-31'), "/tmp/f2016.png")   # before
fetch(l8_truecolor('2016-11-01', '2017-02-12'), "/tmp/f2017.png")   # 2017 pre-fire

try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
except Exception:
    font = ImageFont.load_default()

def label(path, text):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 330, 44], fill=(0, 0, 0))
    d.text((8, 6), text, fill=(255, 255, 0), font=font)
    return im

frames = [label("/tmp/f2016.png", "2016  (before)"),
          label("/tmp/f2017.png", "2017 pre-fire (after)")]
frames[0].save(GIF, save_all=True, append_images=[frames[1]],
               duration=1100, loop=0)
print("saved ->", GIF)
