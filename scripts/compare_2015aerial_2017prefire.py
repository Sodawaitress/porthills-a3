"""
把 2015 航片 和 2017 火前 Landsat 真彩色摆一起，肉眼看变化大不大。
左：2015 航片(0.3m RGB)  右：2017 火前 Landsat(30m, pre_B4/B3/B2)
两张都在本地、都是 EPSG:2193，不用 GEE。
输出：A3/compare_2015_vs_2017.png
"""
import numpy as np, rasterio, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rasterio.windows import from_bounds

# ==== PATHS ====
AERIAL = "/Users/sodawaitress/Desktop/ERST619/A2porthills-fire/raster/PortHills_Aerial03m_2015.tif"
STACK  = "/Users/sodawaitress/Desktop/ERST619/refine/PortHills2017_stack.tif"
OUT    = "/Users/sodawaitress/Desktop/ERST619/A3/compare_2015_vs_2017.png"
# ===============

# --- 2017 火前 Landsat 真彩色（栈里的 pre_B4/B3/B2）---
with rasterio.open(STACK) as ds:
    names = list(ds.descriptions)
    b = [names.index(x) + 1 for x in ("pre_B4", "pre_B3", "pre_B2")]
    rgb17 = ds.read(b).astype("float32")            # (3,H,W) 反射率
    bounds = ds.bounds                              # 用它当共同范围
rgb17 = np.clip(rgb17 / 0.30, 0, 1)                 # 反射率拉伸到 0–1 显示
rgb17 = np.transpose(rgb17, (1, 2, 0))             # → (H,W,3)

# --- 2015 航片，裁到同范围 + 抽稀显示（原图 3 万×3 万，太大）---
with rasterio.open(AERIAL) as ds:
    win = from_bounds(*bounds, transform=ds.transform)
    W = 1200                                        # 目标宽（像元）
    H = int(W * (win.height / win.width))
    aer = ds.read([1, 2, 3], window=win, out_shape=(3, H, W)).astype("float32")
aer = np.transpose(aer, (1, 2, 0))
aer = aer / 255.0 if aer.max() > 1 else aer         # 航片一般是 0–255

# --- 并排画 ---
fig, ax = plt.subplots(1, 2, figsize=(14, 7))
ax[0].imshow(np.clip(aer, 0, 1)); ax[0].set_title("2015 aerial (0.3 m)"); ax[0].axis("off")
ax[1].imshow(rgb17);              ax[1].set_title("2017 pre-fire Landsat (30 m)"); ax[1].axis("off")
plt.tight_layout()
plt.savefig(OUT, dpi=140)
print("saved ->", OUT)
