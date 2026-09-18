# ERST619 A3 — Preliminary Analysis (Port Hills 2017 fire)

Pre-fire vegetation / fuel-type classification of the 2017 Port Hills fire area,
used to test whether unburned refugia relate to vegetation type and terrain.
Due 2026-09-23.

## Start here (for me or for Claude Code)
- **`product.md`** — the working backlog. What to do next, one small task at a time (US1, US2, ...). Open this first.
- **`workflow.md`** — methods / reference / decisions (Claude's manual).
- **`report.md`** — report plan (sections R1–R8, mapped to the marking rubric).

## scripts/
- `kmeans_class_diagnostic.py` — unsupervised k-means on the pre-fire stack; checks whether the 5 classes are spectrally separable (US1.1).
- `01_build_point_table.py` — samples the feature stack at training points into a table (US2; being simplified to sample the existing stack).

## Data (NOT in this repo)
Large rasters/vectors live outside git (school J:\Data drive or OneDrive):
- Pre-fire feature stack `PortHills2017_stack.tif`
- 0.3 m aerial 2015, 8 m DEM
- LCDB (Land Cover Database v5) — reference for labelling classes
Each script has a **`PATHS`** block at the top — edit those paths per machine
(Mac vs school Windows) before running.

## Environment
Python: `rasterio`, `scikit-learn`, `numpy`, `matplotlib`, `earthengine-api`.
