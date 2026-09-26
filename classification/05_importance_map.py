# R5 Step 5: per-class importance (permutation, under spatial-block CV) — substitute for SHAP (package not
# installable offline); Step 6: classification map of the fire area with final S+T+Sp model.
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import StratifiedGroupKFold
exec(open("00_common.py").read())
d, A, names = load(); m = d[d.source == "main"].reset_index(drop=True); cols = SETS["S+T+Sp"]
groups = {"pre-fire spectral": SPEC, "terrain": TERR, "spring 2016": SPR}
feats = {**{g: v for g, v in groups.items()}, **{c: [c] for c in cols}}
rng = np.random.default_rng(1); drops = {f: [] for f in feats}
def recall(y, p): return np.array([(p[y == k] == k).mean() for k in range(4)])
for rep in range(5):
    for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=rep).split(m, m.y, m.block):
        mod = RF(500, max_features="sqrt", random_state=rep, n_jobs=-1).fit(m.loc[tr, cols], m.y[tr])
        Xte = m.loc[te, cols].copy(); yte = m.y[te].values; b = recall(yte, mod.predict(Xte))
        for f, fc in feats.items():
            for _ in range(3):
                Xp = Xte.copy(); perm = rng.permutation(len(Xp)); Xp[fc] = Xte[fc].values[perm]   # permute jointly
                drops[f].append(b - recall(yte, mod.predict(Xp)))
imp = pd.DataFrame({f: np.mean(v, 0) for f, v in drops.items()}, index=CLS).T.round(3)
imp.to_csv("Tab5_10_perm_importance_by_class.csv")
print("== Grouped (drop in class recall) ==\n", imp.loc[list(groups)])
for k in CLS: print(f"\ntop-4 single vars for {k}:\n", imp.loc[cols, k].sort_values(ascending=False).head(4).to_string())
# heatmap
G = imp.loc[list(groups) + cols]
fig, ax = plt.subplots(figsize=(6, 8)); im = ax.imshow(G.values, cmap="Reds", aspect="auto", vmin=0)
ax.set_xticks(range(4)); ax.set_xticklabels(["pasture", "gorse", "broadleaf", "pine"]); ax.set_yticks(range(len(G))); ax.set_yticklabels(G.index, fontsize=8)
ax.axhline(2.5, color="k", lw=1)
for i in range(len(G)):
    for j in range(4): ax.text(j, i, f"{G.values[i,j]:.2f}", ha="center", va="center", fontsize=7)
plt.colorbar(im, label="Drop in class recall when permuted"); ax.set_title("Per-class importance (spatial CV)", fontsize=10)
fig.tight_layout(); fig.savefig("Fig5_4_importance_by_class.png", dpi=300)
# map
final = RF(500, max_features="sqrt", random_state=0, n_jobs=-1).fit(m[cols], m.y)
X = A[..., [names.index(c) for c in cols]]; aoi = A[..., names.index("inside_aoi")] >= 0.5; ok = aoi & np.isfinite(X).all(-1)
Pr = final.predict_proba(X[ok]); cls = np.full(ok.shape, np.nan); cls[ok] = Pr.argmax(1)
conf = np.full(ok.shape, np.nan); conf[ok] = Pr.max(1)
area = pd.Series(cls[ok]).value_counts().sort_index(); area.index = [CLS[int(i)] for i in area.index]
at = pd.DataFrame({"pixels": area, "ha": area * 0.09, "pct": (area / ok.sum() * 100).round(1)}); at.to_csv("Tab5_11_map_area.csv")
np.save("/home/claude/class_map.npy", cls)
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(cls, cmap=ListedColormap([COL[k] for k in CLS]), interpolation="none")
for k in CLS: ax[0].plot([], [], "s", c=COL[k], label=k)
ax[0].legend(fontsize=8, loc="lower left"); ax[0].set_title("(a) RF fuel classes (S+T+Sp), fire area", fontsize=10)
im = ax[1].imshow(conf, cmap="viridis", vmin=.25, vmax=1, interpolation="none"); plt.colorbar(im, ax=ax[1], shrink=.7, label="Max class probability")
ax[1].set_title("(b) Classification confidence", fontsize=10)
for a in ax: a.set_xticks([]); a.set_yticks([])
fig.tight_layout(); fig.savefig("Fig5_5_class_map.png", dpi=250)
print("\n== Map area ==\n", at); print("mean max-prob:", round(np.nanmean(conf), 3), "| share <0.5:", round((conf[ok] < .5).mean(), 3))
