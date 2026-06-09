#!/usr/bin/env python3
"""
Reorganization script: restructures test_subjects/ into optical/<feature>/ directories
with consistent lower-case naming convention: <obj>_<type>_<filter>_<seq>.fits

Run from the pipeline_data root directory:
    python reorganize.py [--dry-run]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
TEST_SUBJECTS = BASE / "test_subjects"

# ---------------------------------------------------------------------------
# New directory structure
# ---------------------------------------------------------------------------

NEW_DIRS = [
    TEST_SUBJECTS / "optical" / "astrometry",
    TEST_SUBJECTS / "optical" / "edge-cases",
    TEST_SUBJECTS / "optical" / "field-calibration",
    TEST_SUBJECTS / "optical" / "photometry",
    TEST_SUBJECTS / "optical" / "runners",
]

# ---------------------------------------------------------------------------
# Complete file mapping: (src_relative_to_test_subjects, dst_relative_to_optical)
# Each entry: (old_path, new_path)  — both relative to test_subjects/
# ---------------------------------------------------------------------------

MAPPING: list[tuple[str, str]] = [
    # ------------------------------------------------------------------
    # optical/astrometry/
    #   NSV 2849 is the primary WCS fixture (specific CD-matrix tests in test_wcs.py)
    #   NSV 3281 is a companion WCS test field observed in the same session
    # ------------------------------------------------------------------
    ("bvr/NSV 2849 1227_13413151_V_000.fits",    "optical/astrometry/nsv2849_star_v_000.fits"),
    ("bvr/NSV 2849_13623547_V_000.fits",          "optical/astrometry/nsv2849_star_v_001.fits"),
    ("bvr/NSV 3281_13623549_V_000.fits",          "optical/astrometry/nsv3281_star_v_000.fits"),

    # ------------------------------------------------------------------
    # optical/photometry/
    #   ngc_3628_hamburer_test is the specific fixture in test-photometry.py
    # ------------------------------------------------------------------
    # Note: _reduced_ suffix distinguishes this pre-reduced frame from the
    # three standard ngc3628 frames in runners/ that share the same obj+type+filter.
    ("bvr/ngc_3628_hamburer_test_12499172_V_0003_reduced.fits",
                                                   "optical/photometry/ngc3628_galaxy_v_reduced_000.fits"),

    # ------------------------------------------------------------------
    # optical/field-calibration/
    #   OCL files: all from ocl/ — exercise Open/Clear/Lum filter substitution (test-ocl.py)
    #   Two BVR files: default and usage-example fixtures for zp_fit.py
    # ------------------------------------------------------------------
    # BVR – ZP fit fixtures
    ("bvr/Carina Nebula V_13835391_V_000.fits",  "optical/field-calibration/carina_nebula_v_000.fits"),
    ("bvr/ngc 2070_V_13690320_V_000.fits",        "optical/field-calibration/ngc2070_nebula_v_000.fits"),

    # OCL – Clear filter
    ("ocl/47 tucanae_14091622_Clear_000.fits",    "optical/field-calibration/47tuc_globular_clear_000.fits"),
    ("ocl/helix nebula_14093330_Clear_000.fits",   "optical/field-calibration/helix_nebula_pn_clear_000.fits"),
    ("ocl/messier 104_14087408_Clear_000.fits",    "optical/field-calibration/m104_galaxy_clear_000.fits"),
    ("ocl/NGC24_14071932_Clear_000.fits",          "optical/field-calibration/ngc24_galaxy_clear_000.fits"),
    ("ocl/ngc 6634_14093328_Clear_000.fits",       "optical/field-calibration/ngc6634_cluster_clear_000.fits"),

    # OCL – Lum filter (M15 seq 000–004 mapped from original _Lum_005 … _Lum_009)
    ("ocl/messier 15_14111493_Lum_005.fits",       "optical/field-calibration/m15_globular_lum_000.fits"),
    ("ocl/messier 15_14111493_Lum_006.fits",       "optical/field-calibration/m15_globular_lum_001.fits"),
    ("ocl/messier 15_14111493_Lum_007.fits",       "optical/field-calibration/m15_globular_lum_002.fits"),
    ("ocl/messier 15_14111493_Lum_008.fits",       "optical/field-calibration/m15_globular_lum_003.fits"),
    ("ocl/messier 15_14111493_Lum_009.fits",       "optical/field-calibration/m15_globular_lum_004.fits"),

    # OCL – Open filter (M15 seq 000–004)
    ("ocl/messier 15_14111493_Open_000.fits",      "optical/field-calibration/m15_globular_open_000.fits"),
    ("ocl/messier 15_14111493_Open_001.fits",      "optical/field-calibration/m15_globular_open_001.fits"),
    ("ocl/messier 15_14111493_Open_002.fits",      "optical/field-calibration/m15_globular_open_002.fits"),
    ("ocl/messier 15_14111493_Open_003.fits",      "optical/field-calibration/m15_globular_open_003.fits"),
    ("ocl/messier 15_14111493_Open_004.fits",      "optical/field-calibration/m15_globular_open_004.fits"),

    # ------------------------------------------------------------------
    # optical/edge-cases/
    #   Three NGC 5286 frames from bad_vals/ with special characters and bad header
    #   values used for edge-case and error-handling tests.
    #   seq 000 = baseline, 001/002 = variants with duplicate-naming artifacts
    # ------------------------------------------------------------------
    ("bad_vals/ngc_5286_12158933.fits",                 "optical/edge-cases/ngc5286_globular_b_000.fits"),
    ("bad_vals/ngc_5286_12158933-2 (1).fits",           "optical/edge-cases/ngc5286_globular_b_001.fits"),
    ("bad_vals/ngc_5286_12158933 (2) (1).fits",         "optical/edge-cases/ngc5286_globular_b_002.fits"),

    # ------------------------------------------------------------------
    # optical/runners/
    #   All remaining BVR files (end-to-end batch pipeline tests via test-optical.py)
    # ------------------------------------------------------------------
    # Andromeda / M31
    ("bvr/andromeda galaxy_13690442_R_001.fits",    "optical/runners/m31_galaxy_r_000.fits"),
    ("bvr/messier 31 V_13111962_V_000.fits",        "optical/runners/m31_galaxy_v_000.fits"),

    # Cat's Paw / NGC 6334  (sorted by obs ID: 13873842 < 13910965)
    ("bvr/cats paw rgb_13873842_V_001.fits",         "optical/runners/ngc6334_nebula_v_000.fits"),
    ("bvr/ngc 6334_13910965_V_032.fits",             "optical/runners/ngc6334_nebula_v_001.fits"),
    ("bvr/ngc 6334_13910965_R_033.fits",             "optical/runners/ngc6334_nebula_r_000.fits"),

    # M8, M16, M20
    ("bvr/M8 V_13900245_V_000.fits",                "optical/runners/m8_nebula_v_000.fits"),
    ("bvr/M16 V_13900241_V_000.fits",               "optical/runners/m16_nebula_v_000.fits"),
    ("bvr/messier 20_V_13690324_V_000.fits",        "optical/runners/m20_nebula_v_000.fits"),

    # M90
    ("bvr/messier 90 galaxy red_13969770_R_000.fits", "optical/runners/m90_galaxy_r_000.fits"),

    # M104 / Sombrero
    ("bvr/sombrero galaxy_13909237_V_015.fits",     "optical/runners/m104_galaxy_v_000.fits"),

    # Neptune, Uranus
    ("bvr/neptune_lab1_V_13497538_V_000.fits",      "optical/runners/neptune_planet_v_000.fits"),
    ("bvr/uranus_lab1v4_V_13497537_V_000.fits",     "optical/runners/uranus_planet_v_000.fits"),

    # NGC 253
    ("bvr/ngc 253 - Lab 4V_13248259_V_002.fits",    "optical/runners/ngc253_galaxy_v_000.fits"),

    # NGC 1846 (star cluster in LMC)
    ("bvr/NGC1846_13895803_R_000.fits",              "optical/runners/ngc1846_cluster_r_000.fits"),

    # NGC 1982 (M43, emission nebula in Orion)
    ("bvr/NGC1982_13873890_R_002.fits",              "optical/runners/ngc1982_nebula_r_000.fits"),

    # NGC 2997  (sorted by obs ID: 13690309 < 13904672 < 13936561 < 13980096)
    ("bvr/ngc 2997_V_13690309_V_000.fits",          "optical/runners/ngc2997_galaxy_v_000.fits"),
    ("bvr/ngc 2997_13904672_V_001.fits",            "optical/runners/ngc2997_galaxy_v_001.fits"),
    ("bvr/ngc 2997_13936561_V_003.fits",            "optical/runners/ngc2997_galaxy_v_002.fits"),
    ("bvr/ngc 2997_13980096_V_006.fits",            "optical/runners/ngc2997_galaxy_v_003.fits"),

    # NGC 3372 (Eta Carina / Keyhole Nebula)
    ("bvr/ngc 3372_13917131_V_005.fits",            "optical/runners/ngc3372_nebula_v_000.fits"),

    # NGC 3628 (Leo Triplet)  (sorted by obs ID: 13869515 < 13891398 < 13906571)
    ("bvr/ngc3628_13869515_V_001.fits",             "optical/runners/ngc3628_galaxy_v_000.fits"),
    ("bvr/ngc 3628_13891398_V_001.fits",            "optical/runners/ngc3628_galaxy_v_001.fits"),
    ("bvr/ngc 3628_13906571_V_001.fits",            "optical/runners/ngc3628_galaxy_v_002.fits"),

    # NGC 5128 / Centaurus A  (B: 13882669 < 13909251; V: 13902003 < 13909242)
    ("bvr/ngc 5128 rgb_13882669_B_001.fits",        "optical/runners/ngc5128_galaxy_b_000.fits"),
    ("bvr/ngc 5128_13909251_B_002.fits",            "optical/runners/ngc5128_galaxy_b_001.fits"),
    ("bvr/ngc 5128_13902003_V_001.fits",            "optical/runners/ngc5128_galaxy_v_000.fits"),
    ("bvr/NGC 5128 V_13909242_V_000.fits",          "optical/runners/ngc5128_galaxy_v_001.fits"),

    # NGC 5286 (globular cluster)
    ("bvr/ngc_5286_12158952_B_0016_reduced.fits",   "optical/runners/ngc5286_globular_b_000.fits"),
    ("bvr/ngc 5286_13878287_V_013.fits",            "optical/runners/ngc5286_globular_v_000.fits"),

    # NGC 5946
    ("bvr/NGC5946_13873866_R_000.fits",             "optical/runners/ngc5946_galaxy_r_000.fits"),

    # NGC 6302 (Bug Nebula, planetary nebula)  (sorted: 13921532 < 13948013)
    ("bvr/ngc 6302_13921532_V_008.fits",            "optical/runners/ngc6302_pn_v_000.fits"),
    ("bvr/ngc 6302_13948013_V_014.fits",            "optical/runners/ngc6302_pn_v_001.fits"),

    # NGC 6634 (open cluster)
    ("bvr/ngc 6634 V_13925958_V_001.fits",          "optical/runners/ngc6634_cluster_v_000.fits"),

    # NGC 7023 (Iris Nebula)
    ("bvr/ngc 7023_14023073_V_011.fits",            "optical/runners/ngc7023_nebula_v_000.fits"),

    # NGC 7048 (planetary nebula)
    ("bvr/ngc7048_13880046_R_000.fits",             "optical/runners/ngc7048_pn_r_000.fits"),

    # NGC 7293 (Helix Nebula, planetary nebula)
    ("bvr/ngc 7293_test_13909269_R_005.fits",       "optical/runners/ngc7293_pn_r_000.fits"),
    ("bvr/ngc 7293_13934854_V_009.fits",            "optical/runners/ngc7293_pn_v_000.fits"),

    # ------------------------------------------------------------------
    # optical/runners/ – narrowband files
    # ------------------------------------------------------------------
    # M42 / Orion Nebula (three observations: NGC 1976 oiii obs 10757808 < M42 oiii obs 12270552)
    ("narrowband/ngc1976oIII_10757808_OIII_000.fits",        "optical/runners/m42_nebula_oiii_000.fits"),
    ("narrowband/m42- OIII_12270552_OIII_000.fits",          "optical/runners/m42_nebula_oiii_001.fits"),
    ("narrowband/orion nebula halpha_8777660_Halpha_000.fits", "optical/runners/m42_nebula_halpha_000.fits"),

    # M51 (Whirlpool Galaxy)
    ("narrowband/M51 OIII_11499671_OIII_000.fits",           "optical/runners/m51_galaxy_oiii_000.fits"),

    # M97 / NGC 3587 (Owl Nebula, planetary nebula) – OIII frame
    ("narrowband/tfn0m419-sq32-20251219-0100-e91.fits",       "optical/runners/m97_pn_oiii_000.fits"),

    # Carina Nebula – OIII (BVR Carina V goes to field-calibration; this narrowband goes to runners)
    ("narrowband/carina OIII_8981892_OIII_000.fits",          "optical/runners/carina_nebula_oiii_000.fits"),

    # NGC 2261 (Hubble's Variable Nebula)
    ("narrowband/lsc0m476-sq34-20251213-0656-e91.fits",       "optical/runners/ngc2261_nebula_oiii_000.fits"),

    # NGC 2489 (open cluster with surrounding H-alpha nebulosity)
    ("narrowband/ngc 2489_14014424_Halpha_009.fits",          "optical/runners/ngc2489_cluster_halpha_000.fits"),

    # NGC 3918 (planetary nebula)
    ("narrowband/lsc0m476-sq34-20251206-0269-e91.fits",       "optical/runners/ngc3918_pn_oiii_000.fits"),

    # M104 / Sombrero – OIII (narrowband; BVR V goes to runners, OCL Clear goes to field-calibration)
    ("narrowband/lsc0m476-sq34-20251217-0382-e91.fits",       "optical/runners/m104_galaxy_oiii_000.fits"),

    # NGC 7293 (Helix) – Halpha
    ("narrowband/ngc 7293_test_13909269_Halpha_002.fits",     "optical/runners/ngc7293_pn_halpha_000.fits"),

    # Polaris (star)
    ("narrowband/polarisHalpha_10104904_Halpha_000.fits",     "optical/runners/polaris_star_halpha_000.fits"),

    # ------------------------------------------------------------------
    # optical/runners/ – SDSS files
    # ------------------------------------------------------------------
    # 47 Tuc (globular cluster)
    ("sdss/coj2m002-ep06-20260128-0068-e91.fits",   "optical/runners/47tuc_globular_gp_000.fits"),
    ("sdss/coj2m002-ep08-20260128-0068-e91.fits",   "optical/runners/47tuc_globular_ip_000.fits"),

    # Abell 36 (planetary nebula)
    ("sdss/ogg2m001-ep02-20260129-0149-e91.fits",   "optical/runners/abell36_pn_rp_000.fits"),
    ("sdss/ogg2m001-ep03-20260129-0154-e91.fits",   "optical/runners/abell36_pn_ip_000.fits"),

    # Horsehead Nebula (emission / reflection nebula in Orion)
    ("sdss/tfn0m419-sq32-20260128-0306-e91.fits",   "optical/runners/horsehead_nebula_rp_000.fits"),

    # IC 3258 (galaxy)
    ("sdss/ogg2m001-ep03-20260127-0147-e91.fits",   "optical/runners/ic3258_galaxy_ip_000.fits"),

    # LDS 987 (galaxy pair)
    ("sdss/tfn0m419-sq32-20260129-0402-e91.fits",   "optical/runners/lds987_galaxy_gp_000.fits"),

    # M97 / NGC 3587 (Owl Nebula, planetary nebula) – SDSS gp frame
    ("sdss/ogg2m001-ep04-20260127-0142-e91.fits",   "optical/runners/m97_pn_gp_000.fits"),

    # NGC 346 (open cluster in SMC)
    ("sdss/coj2m002-ep06-20260128-0065-e91.fits",   "optical/runners/ngc346_cluster_gp_000.fits"),

    # NGC 1300 (barred spiral galaxy)
    ("sdss/coj2m002-ep07-20260129-0068-e91.fits",   "optical/runners/ngc1300_galaxy_rp_000.fits"),

    # NGC 1313 (galaxy)
    ("sdss/coj2m002-ep07-20260129-0065-e91.fits",   "optical/runners/ngc1313_galaxy_rp_000.fits"),

    # NGC 1365 (barred spiral galaxy)
    ("sdss/coj2m002-ep07-20260129-0066-e91.fits",   "optical/runners/ngc1365_galaxy_rp_000.fits"),

    # NGC 1977 (reflection nebula / Running Man, in Orion)
    ("sdss/tfn0m436-sq33-20260128-0325-e91.fits",   "optical/runners/ngc1977_nebula_rp_000.fits"),

    # NGC 3231 (galaxy)
    ("sdss/ogg2m001-ep04-20260127-0143-e91.fits",   "optical/runners/ngc3231_galaxy_gp_000.fits"),

    # NGC 3718 (warped spiral galaxy)
    ("sdss/ogg2m001-ep04-20260127-0146-e91.fits",   "optical/runners/ngc3718_galaxy_gp_000.fits"),

    # NGC 5964 (galaxy)
    ("sdss/ogg2m001-ep03-20260130-0457-e91.fits",   "optical/runners/ngc5964_galaxy_ip_000.fits"),

    # NGC 5985 (galaxy)
    ("sdss/ogg2m001-ep02-20260130-0438-e91.fits",   "optical/runners/ngc5985_galaxy_rp_000.fits"),

    # Pleiades (open cluster)
    ("sdss/tfn0m419-sq32-20260129-0169-e91.fits",   "optical/runners/pleiades_cluster_rp_000.fits"),
]


def build_reverse_map() -> dict[str, str]:
    """Return old_basename -> new_basename for CSV updates."""
    return {
        Path(old).name: Path(new).name
        for old, new in MAPPING
    }


def run(cmd: list[str], dry_run: bool) -> None:
    # Print in a shell-safe form (quote args with spaces)
    display = " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd)
    print(display)
    if not dry_run:
        result = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr}", file=sys.stderr)
            sys.exit(1)


def update_csv(path: Path, reverse_map: dict[str, str], dry_run: bool) -> None:
    """Rewrite the 'file' column in an afterglow CSV using new filenames."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    updated = []
    changed = 0
    for i, line in enumerate(lines):
        if i == 0:
            updated.append(line)
            continue
        parts = line.split(",", 1)
        if not parts:
            updated.append(line)
            continue
        old_name = parts[0].strip()
        new_name = reverse_map.get(old_name)
        if new_name and new_name != old_name:
            updated.append(new_name + "," + parts[1])
            changed += 1
        else:
            updated.append(line)
    if changed:
        print(f"  Updating {path.name}: {changed} filename(s) renamed")
        if not dry_run:
            path.write_text("".join(updated), encoding="utf-8")
    else:
        print(f"  {path.name}: no changes needed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Reorganize pipeline_data test_subjects/")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing them")
    args = parser.parse_args()
    dry_run: bool = args.dry_run

    if dry_run:
        print("=== DRY RUN — no files will be moved ===\n")

    # 1. Validate all source files exist
    missing = [old for old, _ in MAPPING if not (TEST_SUBJECTS / old).exists()]
    if missing:
        print("ERROR: source files not found:")
        for m in missing:
            print(f"  {m}")
        return 1

    # 2. Check for duplicate destinations
    destinations = [new for _, new in MAPPING]
    seen: set[str] = set()
    dupes = [d for d in destinations if d in seen or seen.add(d)]  # type: ignore[func-returns-value]
    if dupes:
        print("ERROR: duplicate destination paths:")
        for d in dupes:
            print(f"  {d}")
        return 1

    # 3. Create new directories (git doesn't track empty dirs; mkdir before git mv)
    print("Creating new directories...")
    for d in NEW_DIRS:
        rel = d.relative_to(BASE)
        if not d.exists():
            print(f"  mkdir -p {rel}")
            if not dry_run:
                d.mkdir(parents=True, exist_ok=True)
        else:
            print(f"  exists: {rel}")

    # 4. Execute git mv for each file
    print("\nMoving and renaming files...")
    for old_rel, new_rel in MAPPING:
        src = f"test_subjects/{old_rel}"
        dst = f"test_subjects/{new_rel}"
        run(["git", "mv", "--", src, dst], dry_run)

    # 5. Update afterglow CSVs
    print("\nUpdating afterglow CSV reference values...")
    reverse_map = build_reverse_map()
    csv_dir = BASE / "afterglow_results"
    for csv_path in sorted(csv_dir.glob("*.csv")):
        update_csv(csv_path, reverse_map, dry_run)

    print("\nDone." + (" (dry run)" if dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
