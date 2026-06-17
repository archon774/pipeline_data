# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a data repository for the Skynet photometric pipeline, used to store test FITS images and pipeline outputs for validating photometric calibration. It lives at `pipeline_data/` within the broader Skynet project (the parent at `/home/claude/skynet/` or similar). Paths in JSON output files reference the full repo path (e.g., `summary_json` fields use `/home/claude/skynet/pipeline_data/...`).

## Scripts

**Rebuild the master zero-point table** (merges per-filter CSVs into one):
```bash
python afterglow_results/build_master_table.py
```

## Data Organization

### Inputs: `test_subjects/optical/`
FITS images reorganized by test use-case into five feature subdirectories.

**Naming convention:** `<object>_<type>_<filter>_<seq>.fits`
- `object` — lower-case object name, spaces → underscores (e.g. `ngc3628`, `m42`, `carina_nebula`)
- `type` — astronomical object type: `galaxy`, `nebula`, `pn` (planetary nebula), `globular`, `cluster`, `star`, `planet`
- `filter` — lower-case filter: `v`, `r`, `b`, `oiii`, `halpha`, `clear`, `lum`, `open`, `gp`, `rp`, `ip`
- `seq` — zero-padded 3-digit sequence number; distinguishes multiple frames of the same object+filter

#### `optical/astrometry/` — 3 files
WCS/astrometry unit-test fixtures.  The NSV 2849 field (2 frames) is the primary target of `test_wcs.py`, which hard-codes the expected CD matrix for this field.
```
nsv2849_star_v_000.fits   ← NSV 2849 1227_13413151_V_000.fits  (primary WCS test)
nsv2849_star_v_001.fits   ← NSV 2849_13623547_V_000.fits
nsv3281_star_v_000.fits   ← NSV 3281_13623549_V_000.fits
```

#### `optical/field-calibration/` — 17 files
OCL filter-substitution fixtures (all 15 from old `ocl/`) plus 2 BVR frames used as the default and usage-example target in `zp_fit.py`.
```
carina_nebula_v_000.fits   ← zp_fit.py usage-example (Carina Nebula V)
ngc2070_nebula_v_000.fits  ← zp_fit.py default FILE variable (ngc 2070_V)
47tuc_globular_clear_000.fits  …  ngc6634_cluster_clear_000.fits  (ocl Clear)
m15_globular_lum_000.fits  …  m15_globular_lum_004.fits           (ocl Lum)
m15_globular_open_000.fits …  m15_globular_open_004.fits          (ocl Open)
```

#### `optical/photometry/` — 1 file
Single pre-reduced fixture for `test-photometry.py`.
```
ngc3628_galaxy_v_reduced_000.fits  ← ngc_3628_hamburer_test_12499172_V_0003_reduced.fits
```
The `_reduced_` infix distinguishes it from the three standard NGC 3628 frames in `runners/`.

#### `optical/edge-cases/` — 3 files
NGC 5286 frames with known pathological header values (bad field-calibration values).  The original filenames contained spaces, parentheses, and dashes that caused edge-case failures.
```
ngc5286_globular_b_000.fits  ← ngc_5286_12158933.fits          (baseline)
ngc5286_globular_b_001.fits  ← ngc_5286_12158933-2 (1).fits   (variant 1)
ngc5286_globular_b_002.fits  ← ngc_5286_12158933 (2) (1).fits (variant 2)
```

#### `optical/runners/` — 67 files
All files used for end-to-end batch pipeline testing (`test-optical.py`, `test-suite.py`, `test_optical_pipeline_processing_run.py`).  Sourced from old `bvr/`, `narrowband/`, and `sdss/` directories.


### Outputs: `afterglow_results/`
Results from the Afterglow photometry web service:
- Per-category CSVs (`afterglow_web_values_bvr.csv`, etc.) — columns: `file`, `Afterglow web zero_point`, `Afterglow web err`
- `afterglow_web_values_master.csv` — consolidated table built by `build_master_table.py`
- `fieldcal/` — full JSON API responses from Afterglow field calibration jobs
- `photometry/` — full photometry source catalogs (CSV) from Afterglow

### Outputs: `zp-fits/`
Local zero-point fitting outputs, one subdirectory per input FITS file:
- `zp_fit.png` / `zp_afterglow_fit.png` — scatter plot of the ZP fit
- `zp_fit_data.csv` / `zp_afterglow_fit_data.csv` — per-source data used in the fit
- `zp_fit_summary.json` / `zp_afterglow_fit_summary.json` — fit metrics and diagnostics
- `ocl_fits/ocl_filter_report.json` — filter selection report for OCL images

## Key Domain Concepts

**Zero point (ZP):** Photometric calibration constant: `catalog_mag = measured_mag + zero_point`. Afterglow internally uses `zero_point = 20` and reports a `zero_point_correction`; the local pipeline computes the absolute ZP directly.

**Slop:** Scatter in the ZP fit (roughly the RMS of residuals after outlier rejection). Lower is better; the pipeline uses slop as the primary quality metric.

**Field calibration:** Matching detected sources to the APASS catalog to compute the ZP. Sources are rejected via Chauvenet's criterion. The fit model is a fixed-slope (`slope = 1.0`) offset: `catalog_mag = measured_mag + ZP`.

**Limmag5 (5σ limiting magnitude):** The faintest detectable magnitude at 5σ confidence, derived from the ZP and background noise.

**OCL filter substitution:** Images taken with Open, Clear, or Lum filters have no direct photometric catalog match. The pipeline trials V, rprime, and R as substitute filters and selects the one yielding the lowest field-calibration slop. Results are recorded in `ocl_filter_report.json`.

**Afterglow vs. local parity check:** `zp_afterglow_fit_summary.json` compares the locally-computed ZP against Afterglow's calibrated ZP. The field `zero_point_within_tolerance` (tolerance = 0.0005 mag) flags whether they agree.

**Pipeline stages:** WCS → Photometry → Field Calibration. If WCS fails (no WCS solution in FITS header), the subsequent stages are skipped.
