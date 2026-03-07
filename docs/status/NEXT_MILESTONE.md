# Next Milestone

- Status date: March 7, 2026
- Default execution target: **M5 — Phase 2 live execution evidence and exit validation for `mriqc_report` and `anat_bold_prep`**

## Milestone Mapping

- Roadmap phase: `docs/ROADMAP.md` Phase 2 — QC and preprocessing
- Implementation-plan milestone: `docs/IMPLEMENTATION-PLAN.md` M5 — Phase 2 live execution evidence and exit validation
- Implementation-sequence boundary: Sprint 5 in `prompts/CODEX_IMPLEMENTATION_SEQUENCE.md`

## Why This Is Now the Current Target

- M4 is now complete at wrapper-contract level: the Phase 2 runtime packages, CLI commands,
  harvesting helpers, fixtures, tests, and status updates are present in the repository.
- The next highest-leverage gap is no longer wrapper shape or benchmark-driver scaffolding; it is
  pinned live execution evidence for MRIQC and fMRIPrep-family preprocessing on public `ds003020`.
- `docs/ROADMAP.md` still requires Phase 2 to be reproducible on benchmark datasets with preserved
  reports and methods metadata before Phase 2 can be treated as exited.

## Required Output Artifacts

- Already present in the repository:
  - `benchmarks/run_phase2_public_mriqc.py`
  - `benchmarks/run_phase2_public_anat_bold_prep.py`
  - `benchmarks/phase2_common.py`
  - `benchmarks/PHASE2_QC_PREP.md`
  - `tests/test_benchmark_artifacts.py` and related benchmark-helper coverage in the default suite
- Still required to exit M5:
  - `benchmarks/artifacts/phase2_ds003020_mriqc/`: checked-in manifests, logs, reports,
    provenance files, preserved QC outputs, and benchmark metadata from a real live run
  - `benchmarks/artifacts/phase2_ds003020_anat_bold_prep/`: checked-in manifests, logs, reports,
    provenance files, preserved preprocessing outputs, and benchmark metadata from a real live run
  - `docs/status/`: updated evidence, blocker retirement, and milestone reality after the live run

## Explicitly Out of Scope

- Phase 3 work: `task_glm`, `rest_connectivity`, `report_bundle`, `repro_bundle`
- Phase 4 work: `diffusion_prep`
- publication freeze, DOI work, or JOSS packaging

## Exit Criteria

- At least one pinned MRIQC path and one pinned anat/BOLD preprocessing path have checked-in
  benchmark artifacts for public `ds003020` with exact commands, manifests, and reproducibility
  files.
- Live execution evidence preserves upstream report locations, derivative metadata, and
  fMRIPrep-family boilerplate in machine-readable manifests.
- Runtime availability is demonstrated by concrete commands in a reproducible environment, not by
  request rendering alone.
- Tests and docs cover the benchmark harness and checked-in artifacts, and the status files cite
  real repository evidence.
