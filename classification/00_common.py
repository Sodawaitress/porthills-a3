# Shared loader for R5: reference samples + features at cells; pixel feature matrix
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude")
from A3_R4_regression_io import read_stack
UP = "/mnt/user-data/uploads/"
CLS = ["pasture", "gorse_broom", "broadleaf_scrub", "exotic_pine"]
COL = {"pasture": "#d4a017", "gorse_broom": "#c0392b", "broadleaf_scrub": "#27ae60", "exotic_pine": "#1f4e79"}
SPEC = ["pre_B2","pre_B3","pre_B4","pre_B5","pre_B6","pre_B7","NDVI","NDMI","BSI","NBR_pre"]
TERR = ["elev","slope","northness"]            # no grid_row/grid_col (Meyer et al. 2019)
SPR  = ["spr_B2","spr_B3","spr_B4","spr_B5","spr_B6","spr_B7","NDVI_spr","YI_spr","dNDVI_spr_sum"]
SETS = {"S": SPEC, "S+T": SPEC+TERR, "S+Sp": SPEC+SPR, "S+T+Sp": SPEC+TERR+SPR}
def load():
    S, n = read_stack(UP+"PortHills2017_stack.tif"); P, pn = read_stack(UP+"PortHills2016_spring.tif")
    A = np.concatenate([S, P], -1); names = n + pn
    df = pd.read_csv(UP+"A3_reference_cells.csv"); d = df[df.use_A3].copy()
    r, c = d.array_row.values, d.array_col.values
    for i, b in enumerate(names): d[b] = A[r, c, i]
    d["block"] = (r // 10).astype(str) + "_" + (c // 10).astype(str)   # 300 m blocks
    d["y"] = d.FuelClass.map({k: i for i, k in enumerate(CLS)})
    return d, A, names
