# R5 Steps 3-4: RF, 4 feature sets; spatial-block CV on main 171 (5-fold x 20 repeats, 300 m blocks);
# original split train->valid; final model on main -> expansion 88 independent test. No Kappa (Foody 2020).
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import confusion_matrix
def proportion_confint(k, n, method="wilson", z=1.96):
    p = k / n; c = (p + z*z/(2*n)) / (1 + z*z/n); h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n); return c - h, c + h
exec(open("00_common.py").read())
d, A, names = load(); m = d[d.source == "main"].reset_index(drop=True); e = d[d.source != "main"].reset_index(drop=True)
rf = lambda s: RF(500, max_features="sqrt", random_state=s, n_jobs=-1)
def acc(cm):
    oa = np.trace(cm) / cm.sum(); pa = np.diag(cm) / cm.sum(1); ua = np.diag(cm) / cm.sum(0); return oa, pa, ua
R = 20; res = []; cms = {}
for name, cols in SETS.items():
    cm_tot = np.zeros((4, 4), int)
    for rep in range(R):
        pred = np.empty(len(m), int)
        for tr, te in StratifiedGroupKFold(5, shuffle=True, random_state=rep).split(m, m.y, m.block):
            pred[te] = rf(rep).fit(m.loc[tr, cols], m.y[tr]).predict(m.loc[te, cols])
        cm = confusion_matrix(m.y, pred, labels=range(4)); cm_tot += cm; oa, pa, ua = acc(cm)
        res.append([name, rep, oa, *pa, *ua])
    cms[name] = cm_tot
cv = pd.DataFrame(res, columns=["set", "rep", "OA"] + [f"PA_{k}" for k in CLS] + [f"UA_{k}" for k in CLS])
cv.to_csv("Tab5_6_cv_by_repeat.csv", index=False)
S1 = cv.groupby("set", sort=False).agg(["mean", "std"]).drop(columns="rep").round(3); S1.to_csv("Tab5_7_cv_summary.csv")
base = cv[cv.set == "S"].OA.values
diff = {k: (cv[cv.set == k].OA.values - base) for k in SETS}
print("== Spatial-block CV (main 171, 5-fold x 20) =="); print(S1[[("OA", "mean"), ("OA", "std")] + [(f"PA_{k}", "mean") for k in CLS]].to_string())
print("OA gain vs S: mean, share of repeats >0:", {k: (round(v.mean(), 3), round((v > 0).mean(), 2)) for k, v in diff.items()})
# original split
orig = []
for name, cols in SETS.items():
    tr, va = m[m.split == "train"], m[m.split == "valid"]
    p = np.mean([rf(s).fit(tr[cols], tr.y).predict(va[cols]) == va.y for s in range(10)], 0)
    orig.append([name, len(tr), len(va), p.mean()])
print("\n== Original 300 m split (train -> valid, 10 seeds) =="); print(pd.DataFrame(orig, columns=["set", "n_tr", "n_va", "OA"]).round(3))
# independent test
near = e.dist_to_main_m < 90; rows = []; ecm = {}
for name, cols in SETS.items():
    P = np.array([rf(s).fit(m[cols], m.y).predict_proba(e[cols]) for s in range(10)]).mean(0); pr = P.argmax(1)
    cm = confusion_matrix(e.y, pr, labels=range(4)); ecm[name] = cm; oa, pa, ua = acc(cm)
    k = int(np.trace(cm)); lo, hi = proportion_confint(k, len(e), method="wilson")
    oa_far = (pr[~near] == e.y[~near]).mean()
    rows.append([name, oa, lo, hi, oa_far, *pa, *ua])
    if name == "S+T+Sp": e["pred"] = pr
ET = pd.DataFrame(rows, columns=["set", "OA", "OA_lo95", "OA_hi95", "OA_far(>=90m,n=71)"] + [f"PA_{k}" for k in CLS] + [f"UA_{k}" for k in CLS]).round(3)
ET.to_csv("Tab5_8_expansion_test.csv", index=False)
print("\n== Independent test: expansion 88 =="); print(ET.iloc[:, :5].to_string()); print(ET[["set"] + [f"PA_{k}" for k in CLS]].to_string())
for name in ["S", "S+T+Sp"]:
    for tag, cm in [("cv", cms[name]), ("test", ecm[name])]:
        pd.DataFrame(cm, index=[f"ref_{k}" for k in CLS], columns=[f"map_{k}" for k in CLS]).to_csv(f"Tab5_9_confusion_{tag}_{name.replace('+','_')}.csv")
print("\nCV confusion (pooled 20 reps), S+T+Sp:\n", pd.DataFrame(cms["S+T+Sp"], index=CLS, columns=CLS))
print("Test confusion, S+T+Sp:\n", pd.DataFrame(ecm["S+T+Sp"], index=CLS, columns=CLS))
print("Test confusion, S:\n", pd.DataFrame(ecm["S"], index=CLS, columns=CLS))
