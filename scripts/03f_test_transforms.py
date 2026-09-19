import pandas as pd
import numpy as np
from scipy import stats

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

# worst offenders found in the per-class normality check
targets = [
    ("native_scrub", "NBR_pre"),
    ("native_scrub", "NDVI"),
    ("native_scrub", "BSI"),
    ("exotic_pine", "pre_B4"),
    ("exotic_pine", "pre_B2"),
    ("gorse_broom", "pre_B7"),
]

def skew_kurt(x):
    return stats.skew(x), stats.kurtosis(x)

print(f"{'class':13s} {'var':8s} {'transform':10s} {'skew':>8s} {'kurt':>8s}")
for cls, var in targets:
    x = df.loc[df["FuelClass"] == cls, var].values
    sk0, ku0 = skew_kurt(x)
    print(f"{cls:13s} {var:8s} {'raw':10s} {sk0:8.3f} {ku0:8.3f}")

    if (x > 0).all():
        sk, ku = skew_kurt(np.log(x))
        print(f"{'':13s} {'':8s} {'log':10s} {sk:8.3f} {ku:8.3f}")
        sk, ku = skew_kurt(np.sqrt(x))
        print(f"{'':13s} {'':8s} {'sqrt':10s} {sk:8.3f} {ku:8.3f}")
    else:
        print(f"{'':13s} {'':8s} {'log/sqrt':10s} {'skip (有负值/0)':>18s}")

    z = (x - x.mean()) / x.std()
    sk, ku = skew_kurt(z)
    print(f"{'':13s} {'':8s} {'z-score':10s} {sk:8.3f} {ku:8.3f}  (z标准化不改变分布形状，偏度峰度理论上应该跟raw一样，这里算出来只是确认)")
    print()
