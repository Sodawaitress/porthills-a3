# R5 Step 2: unsupervised exploration (Lab 5): z-score -> PCA -> K-means on all fire-area pixels
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler; from sklearn.decomposition import PCA
from sklearn.cluster import KMeans; from sklearn.metrics import silhouette_score, adjusted_rand_score
exec(open("00_common.py").read())
d, A, names = load(); cols = SETS["S+T+Sp"]; idx = [names.index(c) for c in cols]
X = A[..., idx]; aoi = A[..., names.index("inside_aoi")] >= 0.5
ok = aoi & np.isfinite(X).all(-1); Xp = X[ok]
sc = StandardScaler().fit(Xp); Z = sc.transform(Xp)
pca = PCA().fit(Z); ev = pca.explained_variance_ratio_; cum = ev.cumsum(); npc = int(np.searchsorted(cum, .90) + 1)
P = pca.transform(Z)[:, :npc]
rng = np.random.default_rng(0); sub = rng.choice(len(P), 4000, replace=False); sil = {}
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(P); sil[k] = silhouette_score(P[sub], km.labels_[sub])
km4 = KMeans(4, n_init=10, random_state=0).fit(P)
m = d[d.source == "main"]; Zm = pca.transform(sc.transform(m[cols].values))[:, :npc]
lab = km4.predict(Zm); ct = pd.crosstab(m.FuelClass, lab).reindex(CLS); ari = adjusted_rand_score(m.FuelClass, lab)
ct.to_csv("Tab5_4_kmeans4_vs_fuel.csv")
load_ = pd.DataFrame(pca.components_[:3].T, index=cols, columns=["PC1", "PC2", "PC3"]).round(2); load_.to_csv("Tab5_5_PCA_loadings.csv")
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
ax[0].bar(range(1, 11), ev[:10] * 100); ax[0].plot(range(1, 11), cum[:10] * 100, "k-o", ms=3)
ax[0].set_title("(a) PCA explained variance (%)", fontsize=10); ax[0].set_xlabel("PC")
ax[1].plot(list(sil), list(sil.values()), "-o"); ax[1].set_title("(b) K-means silhouette", fontsize=10); ax[1].set_xlabel("k")
Pm = pca.transform(sc.transform(m[cols].values))
for k in CLS: s = m.FuelClass.values == k; ax[2].scatter(Pm[s, 0], Pm[s, 1], s=14, c=COL[k], label=k, alpha=.8)
ax[2].set_xlabel(f"PC1 ({ev[0]*100:.0f}%)"); ax[2].set_ylabel(f"PC2 ({ev[1]*100:.0f}%)"); ax[2].legend(fontsize=7, frameon=False)
ax[2].set_title("(c) Reference cells in PC1–PC2", fontsize=10)
for a in ax: a.grid(alpha=.3)
fig.tight_layout(); fig.savefig("Fig5_3_pca_kmeans.png", dpi=300)
img = np.full(ok.shape, np.nan); img[ok] = km4.labels_; np.save("/home/claude/kmeans4.npy", img)
print("pixels", ok.sum(), "| PCs for 90%:", npc, "| ev:", (ev[:5] * 100).round(1))
print("silhouette:", {k: round(v, 3) for k, v in sil.items()}); print(ct); print("ARI:", round(ari, 3)); print(load_)
