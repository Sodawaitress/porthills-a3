# ============================================================
# Canterbury 0.2m Rural Aerial 2024 (LINZ 121056) tiles -> single RGB,
# clipped to the 2024 Port Hills fire (bbox + margin), EPSG:2193.
# 照 A2porthills-fire/merge_aerial.py 的做法：WarpedVRT 统一 WKT + JPEG + overviews。
# 用途：2024 火场高分参考底图（判读/看 pre-post）。非分类器输入(RGB无NIR)。
# ============================================================
import rasterio, glob, os, geopandas as gpd
from rasterio.merge import merge
from rasterio.vrt import WarpedVRT
from rasterio.crs import CRS
from rasterio.enums import Resampling

TILES = "_lds_check/tifs/*.tif"                 # 已抽出的覆盖火场瓦片(0602/0603)
FB    = "2024_materials/boundary/Approximate Fire Extent 180224.shp"
OUT   = "PortHills_Aerial02m_2024_fireclip.tif"
MARGIN = 300                                    # 火场外留 300m 边

paths = sorted(glob.glob(TILES)); assert paths, "没找到抽出的 tif"
print("tiles:", [os.path.basename(p) for p in paths])

b = gpd.read_file(FB).to_crs(2193).total_bounds  # L,B,R,T
win = (b[0]-MARGIN, b[1]-MARGIN, b[2]+MARGIN, b[3]+MARGIN)

NZTM = CRS.from_epsg(2193)                       # 各瓦片 WKT 略不同 -> 统一
srcs = [rasterio.open(p) for p in paths]
vrts = [WarpedVRT(s, crs=NZTM) for s in srcs]
arr, tf = merge(vrts, bounds=win, indexes=[1, 2, 3], nodata=0)  # RGB(丢alpha)
print("mosaic:", arr.shape[2], "x", arr.shape[1], "bands", arr.shape[0])

meta = dict(driver='GTiff', height=arr.shape[1], width=arr.shape[2], count=3,
            dtype='uint8', crs='EPSG:2193', transform=tf, nodata=0,
            tiled=True, blockxsize=512, blockysize=512,
            compress='JPEG', photometric='YCBCR', jpeg_quality=90, interleave='pixel')
with rasterio.open(OUT, 'w', **meta) as dst:
    dst.write(arr)
    dst.build_overviews([2, 4, 8, 16], Resampling.average)

mb = os.path.getsize(OUT)/1e6
with rasterio.open(OUT) as c:
    print(f"wrote {OUT} ({mb:.0f} MB)  size {c.width}x{c.height}  bounds {[round(v) for v in c.bounds]}")
