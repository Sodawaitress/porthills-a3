import pandas as pd

CSV = r"C:\Users\zhouy3d\Desktop\a3\scripts\PortHills_PointTable.csv"
df = pd.read_csv(CSV)

RENAME = {c: c.replace("PortHills2017_stack_", "") for c in df.columns if c.startswith("PortHills2017_stack_")}
df = df.rename(columns=RENAME)

COLS = ["pre_B2", "pre_B3", "pre_B4", "pre_B5", "pre_B6", "pre_B7",
        "NDVI", "BSI", "NBR_pre", "elev", "slope", "northness"]

print("=== 重复行 ===")
dup_mask = df.duplicated(subset=COLS, keep=False)
print(df.loc[dup_mask, ["FuelClass", "split"] + COLS])

print("\n=== 逐列离群值明细 ===")
for c in ["slope", "pre_B5", "pre_B7", "pre_B2", "pre_B6"]:
    q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (df[c] < lo) | (df[c] > hi)
    print(f"\n--- {c} (fence: {lo:.3f} ~ {hi:.3f}) ---")
    print(df.loc[mask, ["FuelClass", "split", c]])
