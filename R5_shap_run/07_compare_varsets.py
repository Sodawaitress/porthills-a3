"""
R5 — pick the main model: compare 4 RF variable sets on the SAME spatial-block CV.
Same 171 points, same 300 m blocks, same 5-fold StratifiedGroupKFold as 06_shap_local.py.
Reports out-of-fold OA / Kappa (mean over folds) + per-class PA/UA for each set.
Run:  python3 07_compare_varsets.py
"""
import os, sys, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from A3_R4_regression_io import read_stack

CLS  = ["pasture", "gorse_broom", "broadleaf_scrub", "exotic_pine"]
SPEC = ["pre_B2","pre_B3","pre_B4","pre_B5","pre_B6","pre_B7","NDVI","NDMI","BSI","NBR_pre"]
TERR = ["elev","slope","northness"]
SPR  = ["spr_B2","spr_B3","spr_B4","spr_B5","spr_B6","spr_B7","NDVI_spr","YI_spr","dNDVI_spr_sum"]
SETS = {"S (spectral only)": SPEC,
        "S+T (+terrain)":     SPEC+TERR,
        "S+Sp (+spring)":     SPEC+SPR,
        "S+T+Sp (all)":       SPEC+TERR+SPR}

S, n  = read_stack(os.path.join(HERE, "PortHills2017_stack.tif"))
P, pn = read_stack(os.path.join(HERE, "PortHills2016_spring.tif"))
A = np.concatenate([S, P], -1); names = list(n) + list(pn)
df = pd.read_csv(os.path.join(HERE, "A3_reference_cells.csv"))
m = df[df.use_A3 & (df.source == "main")].reset_index(drop=True)
r, c = m.array_row.values, m.array_col.values
for i, b in enumerate(names): m[b] = A[r, c, i]
m["block"] = (r // 10).astype(str) + "_" + (c // 10).astype(str)
y = m.FuelClass.map({k: i for i, k in enumerate(CLS)}).values
print("samples:", len(m), dict(m.FuelClass.value_counts()), "\n")

def cv(cols):
    X = m[cols].values; yhat = np.full(len(m), -1)
    for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=0).split(X, y, m.block):
        mod = RF(500, max_features="sqrt", random_state=0, n_jobs=-1).fit(X[tr], y[tr])
        yhat[te] = mod.predict(X[te])
    oa = accuracy_score(y, yhat); k = cohen_kappa_score(y, yhat)
    cm = confusion_matrix(y, yhat, labels=range(4))
    pa = [cm[i, i] / cm[i, :].sum() if cm[i, :].sum() else np.nan for i in range(4)]
    ua = [cm[i, i] / cm[:, i].sum() if cm[:, i].sum() else np.nan for i in range(4)]
    return oa, k, pa, ua

print(f"{'variable set':22s} {'n_vars':>6s} {'OA':>6s} {'Kappa':>6s}   per-class PA (pas/gor/bro/pin)")
best = None
for tag, cols in SETS.items():
    oa, k, pa, ua = cv(cols)
    print(f"{tag:22s} {len(cols):6d} {oa:6.3f} {k:6.3f}   " + " ".join(f"{p:.2f}" for p in pa))
    if best is None or oa > best[1]: best = (tag, oa, k)

print(f"\nhighest OA: {best[0]}  (OA={best[1]:.3f}, Kappa={best[2]:.3f})")
print("note: all use out-of-fold predictions on the same 171 pts / 300 m blocks,")
print("      so these OA numbers ARE directly comparable to each other.")
