# Active Blockers

- Status date: March 8, 2026
- Impacted milestone: `docs/status/NEXT_MILESTONE.md` (`M5 — Phase 2 live execution evidence and exit validation`)

## B1 — Live Phase 2 runtimes are unavailable in the inspected workspace

- Evidence:
  - `docker --version` returned `command not found` on March 7, 2026.
  - `apptainer --version` returned `command not found` on March 7, 2026.
  - `mriqc --version` returned `command not found` on March 7, 2026.
  - `fmriprep --version` returned `command not found` on March 7, 2026.
  - `/tmp/clawneuro-plan/bin/python benchmarks/run_phase2_public_mriqc.py --help` and
    `/tmp/clawneuro-plan/bin/python benchmarks/run_phase2_public_anat_bold_prep.py --help`
    succeeded on March 7, 2026, confirming the harness exists even though the runtime does not.
- Impact:
  - M5 benchmark execution cannot be verified locally in this workspace even though wrapper
    contracts, benchmark drivers, and provenance hardening are implemented.
- Unblock condition:
  - run the next milestone in a reproducible environment that provides Docker or Apptainer access
    to pinned upstream images, or pinned local MRIQC / fMRIPrep installations plus equivalent
    provenance capture.

## B2 — The selected public benchmark dataset is not present in the inspected workspace

- Evidence:
  - `find . -maxdepth 3 \\( -type d -o -type f \\) -name '*ds003020*'` returned no results on
    March 8, 2026.
- Impact:
  - The repository now contains the benchmark harness for the pinned `ds003020`
    `sub-UTS01/ses-1` subset, but the live run cannot be started locally because that dataset root
    is absent.
- Unblock condition:
  - execute the benchmark drivers in an environment that provides a local `ds003020` BIDS root or
    subset root matching the pinned benchmark files to pass through `--dataset-root`.

## Monitoring note

- Retire this blocker only after the repository contains checked-in Phase 2 live execution evidence
  and the verifying runtime-availability commands plus the selected dataset root can be cited from
  the environment that produced it.
