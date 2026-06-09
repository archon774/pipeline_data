# test_subjects/ Organization

All files live under `test_subjects/optical/`, split into five subdirectories by **testing purpose**:

## `optical/astrometry/` — 3 files
WCS/astrometry unit-test fixtures. These are the specific frames that `test_wcs.py` references by name and whose CD matrix values are hard-coded into that test. They're isolated here so it's clear they're not general-purpose inputs.

## `optical/field-calibration/` — 17 files
Fixtures for testing the OCL filter-substitution logic and the zero-point fitting scripts (`zp_fit.py`). Includes the two BVR frames that serve as `zp_fit.py`'s default and usage-example targets, plus the 15 OCL (Open/Clear/Lum) frames used to validate filter substitution across a range of object types.

## `optical/photometry/` — 1 file
A single pre-reduced frame (`ngc3628_galaxy_v_reduced_000.fits`) used specifically by `test-photometry.py`. The `_reduced_` infix in the filename distinguishes it from the three raw NGC 3628 frames that live in `runners/`.

## `optical/edge-cases/` — 3 files
Three NGC 5286 frames with known pathological FITS headers (bad field-calibration values). Their originals had filenames with spaces, parentheses, and dashes — characters that previously caused pipeline failures. They're isolated here to make it obvious these are adversarial inputs, not normal data.

## `optical/runners/` — 67 files
The bulk of the data. Used for end-to-end batch pipeline testing (`test-optical.py`, `test-suite.py`, `test_optical_pipeline_processing_run.py`). Covers a wide variety of object types, filters, and multi-frame sequences to exercise the full pipeline breadth.

---

## Why organized this way

The key design principle is **grouping by test use-case, not by data type**. The old structure (pre-reorganization) grouped by filter category (`bvr/`, `narrowband/`, `sdss/`, `ocl/`), which was natural from a data-collection perspective but made it hard to know which tests used which files.

The current layout makes a few things immediately clear:
- **Traceability**: you can find the fixtures for a specific test script by going to the matching subdirectory.
- **Intent signaling**: edge-case inputs are visually separated from normal inputs, so they won't be accidentally included in batch runs that expect clean data.
- **Naming consistency**: every file follows `<object>_<type>_<filter>_<seq>.fits` (all lower-case, spaces as underscores), replacing the original inconsistent Skynet-generated filenames that mixed cases, spaces, and special characters.
