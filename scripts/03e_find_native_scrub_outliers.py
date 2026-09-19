import pandas as pd

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)
RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

ns = df[df["FuelClass"] == "native_scrub"].copy()
ns = ns.sort_values("NBR_pre")
print("native_scrub 按 NBR_pre 从低到高排序（最可疑的在最上面）:")
print(ns[["X", "Y", "NDVI", "NBR_pre", "BSI", "split"]].head(6).to_string(index=False))
