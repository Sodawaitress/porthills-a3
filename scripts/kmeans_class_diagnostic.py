"""
US1.1 diagnostic - unsupervised k-means.
Clusters pre-fire spectral pixels (no labels) to check whether the intended
5 vegetation/fuel classes are spectrally separable before collecting labels.

Run:     python3 kmeans_class_diagnostic.py
Outputs: <OUT>/kmeans_k{5,6,7}.png|.tif, profile_k*.png, fingerprint_k*.csv
"""
import numpy as np, rasterio, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# ==== PATHS (edit per machine) ====
STACK = "/Users/sodawaitress/Desktop/ERST619/refine/PortHills2017_stack.tif"
OUT   = Path("/Users/sodawaitress/Desktop/ERST619/A3/kmeans_diagnostic")
# ==================================

KS = [5, 6, 7]            # compare cluster counts
USE_TERRAIN = False       # spectral-only by default

OUT.mkdir(exist_ok=True)

# pre-fire vegetation features, matched by band name
FEATURES = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7", "NDVI", "BSI"]
if USE_TERRAIN:
    FEATURES += ["elev", "slope", "northness"]

with rasterio.open(STACK) as ds:
    names = list(ds.descriptions)
    idx   = [names.index(f) + 1 for f in FEATURES]   # rasterio bands are 1-based
    arr   = ds.read(idx).astype("float32")
    valid = ds.read(names.index("valid_data") + 1)   # 1 = valid pixel
    profile = ds.profile

feat, H, W = arr.shape
X = arr.reshape(feat, -1).T

# valid mask: valid_data > 0 and finite features (drop cloud holes / nodata)
mask = (valid.reshape(-1) > 0) & np.isfinite(X).all(axis=1)
Xv = X[mask]

# standardise: k-means uses distance, so unscaled bands would dominate
Xs = StandardScaler().fit_transform(Xv)

profile.update(count=1, dtype="int16", nodata=-1)

for k in KS:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xs)

    labels = np.full(H * W, -1, dtype="int16")       # -1 = invalid / background
    labels[mask] = km.labels_
    lab2d = labels.reshape(H, W)

    # cluster map GeoTIFF (overlay on 0.3 m aerial to identify clusters)
    with rasterio.open(OUT / f"kmeans_k{k}.tif", "w", **profile) as dst:
        dst.write(lab2d, 1)

    # cluster map PNG
    disp = np.ma.masked_less(lab2d, 0)
    plt.figure(figsize=(6, 6))
    plt.imshow(disp, cmap="tab10")
    plt.title(f"k-means  k={k}  (pre-fire spectral)")
    plt.colorbar(ticks=range(k), label="cluster")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUT / f"kmeans_k{k}.png", dpi=140)
    plt.close()

    # per-cluster fingerprint (means in original units) to help label clusters
    means = np.vstack([Xv[km.labels_ == c].mean(axis=0) for c in range(k)])
    with open(OUT / f"fingerprint_k{k}.csv", "w") as f:
        f.write("cluster,count," + ",".join(FEATURES) + "\n")
        for c in range(k):
            row = ",".join(f"{v:.4f}" for v in means[c])
            f.write(f"{c},{int((km.labels_ == c).sum())},{row}\n")

    # per-cluster spectral profile (pre-fire bands): shows which clusters overlap
    bands = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7"]
    bidx = [FEATURES.index(b) for b in bands]
    plt.figure(figsize=(7, 4.5))
    for c in range(k):
        plt.plot(range(6), means[c][bidx], marker="o", label=f"c{c}")
    plt.xticks(range(6), ["B2", "B3", "B4", "B5", "B6", "B7"])
    plt.xlabel("Landsat band"); plt.ylabel("mean reflectance")
    plt.title(f"per-cluster spectral profile  k={k}")
    plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
    plt.savefig(OUT / f"profile_k{k}.png", dpi=140); plt.close()

    uniq, cnt = np.unique(km.labels_, return_counts=True)
    print(f"k={k}: " + ", ".join(f"c{u}={c}px" for u, c in zip(uniq, cnt)))

print("done ->", OUT)
