# Implementation Plan

## Summary

ClawNeuro has completed the shared foundation, the Phase 1 skill contract layer, the M3
hardening/benchmark validation step, and the M4 Phase 2 wrapper baseline. The repository now
contains typed `mriqc_report` and `anat_bold_prep` runtime packages, preserved upstream-artifact
harvesting helpers, CLI entry points, and synthetic Phase 2 fixtures/tests.

The next implementation target is M5: move from contract-complete Phase 2 wrappers to a
repository-complete live-evidence path for MRIQC and fMRIPrep-family runs on public `ds003020`,
without skipping ahead to downstream analysis skills. In this workspace, the repository-prep
portion of M5 is implementable now, while the final live benchmark run remains blocked until Docker
or Apptainer plus the selected public dataset are available in a reproducible environment.

## Milestones

### M0. Documentation and governance baseline

- Maintain `docs/IMPLEMENTATION-PLAN.md`, `docs/RISK-REGISTER.md`, and `docs/TEST-STRATEGY.md` as
  the authoritative execution baseline.
- Keep `README.md`, `tests/README.md`, and skill contracts synchronized with implementation status.
- Replace remaining placeholder org metadata before public release.

Quality gate:
- docs reflect the actual code surface, benchmark evidence, and known risks.

### M1. Shared foundation

File targets:
- `src/clawneuro/core/`
- `src/clawneuro/provenance/`
- `src/clawneuro/reporting/`
- `src/clawneuro/orchestrator/`
- `src/clawneuro/cli/`

Deliverables:
- typed run status, artifact, provenance, and manifest models;
- shared config loading for YAML/JSON/TOML;
- execution planning for local, Docker, and Apptainer backends;
- canonical run-directory layout and BIDS helper utilities;
- deterministic reporting and reproducibility-bundle writing.

Quality gate:
- unit tests cover model validation, serialization, layout, reporting, and provenance behavior.

### M2. Phase 1 skill contract layer

File targets:
- `src/clawneuro/skills/bids_auditor/`
- `src/clawneuro/skills/dicom_to_bids/`
- `src/clawneuro/skills/deid_check/`
- `skills/bids_auditor/`
- `skills/dicom_to_bids/`
- `skills/deid_check/`

Deliverables:
- `bids_auditor` dry-run and executable validator command planning with normalized summaries;
- `dicom_to_bids` wrapped curation planning with manifest-backed outputs;
- `deid_check` conservative export-readiness assessment with policy-traceable results.

Quality gate:
- contract tests cover input validation, output files, warnings, and provenance minimums.

### M3. Phase 1 execution hardening and exit validation

Status:
- observed complete on March 7, 2026

File targets:
- `src/clawneuro/core/execution.py`
- `src/clawneuro/skills/bids_auditor/`
- `src/clawneuro/skills/dicom_to_bids/`
- `src/clawneuro/skills/deid_check/`
- `.github/workflows/python-tests.yml`
- `benchmarks/`
- `docs/status/`

Deliverables:
- documented editable-install developer path for Python 3.11+;
- Python 3.11 CI coverage for editable install, tests, and CLI smoke checks;
- stable Docker and Apptainer bind-mount planning rooted at `/clawneuro/input`,
  `/clawneuro/output`, and `/clawneuro/config`;
- runtime evidence capture for `dicom_to_bids`, including resolved executables and versions;
- public-case `dcm_qa_nih` benchmark evidence with exact commands, checksums, reports, and
  manifests under `benchmarks/artifacts/phase1_dcm_qa_nih/`;
- status updates that cite real artifacts instead of blocked intent.

Quality gate:
- a clean Python 3.11+ or 3.14 environment passes the default test suite;
- `bids_auditor` retains public validator fidelity coverage;
- `dicom_to_bids` has successful public-case evidence with reproducible provenance;
- `deid_check` emits policy-traceable rule results;
- status files cite concrete benchmark artifacts, commands, tests, and unresolved risks.

### M4. Phase 2 wrapper baseline

Status:
- observed complete on March 7, 2026

File targets:
- `src/clawneuro/skills/mriqc_report/`
- `src/clawneuro/skills/anat_bold_prep/`
- `skills/mriqc_report/`
- `skills/anat_bold_prep/`
- `src/clawneuro/core/execution.py`
- `src/clawneuro/reporting/`
- `containers/`
- `tests/`
- `docs/status/`

Deliverables:
- typed configs and result contracts for `mriqc_report` and `anat_bold_prep`;
- container-backed request planning that keeps pinned images explicit;
- upstream report harvesting hooks and deterministic references in run manifests;
- boilerplate/version capture for MRIQC and fMRIPrep-family outputs;
- CLI entry points and contract tests for planned and stubbed execution paths.

Quality gate:
- no Phase 3 or Phase 4 work starts before these wrappers exist at contract level;
- new execution paths preserve exact commands, image references, logs, and report locations;
- tests cover container request shape, report harvesting behavior, and manifest serialization.

### M5. Phase 2 live execution evidence and exit validation

File targets:
- `benchmarks/`
- `containers/`
- `src/clawneuro/skills/mriqc_report/`
- `src/clawneuro/skills/anat_bold_prep/`
- `docs/status/`

Deliverables:
- pinned live-execution path for `mriqc_report` in a container-capable environment;
- pinned live-execution path for `anat_bold_prep` in a container-capable environment;
- public-case Phase 2 target fixed to `ds003020` participant `01` with anatomical and BOLD
  coverage;
- Docker as the default benchmark backend, with Apptainer supported as the fallback execution path;
- benchmark drivers and shared helpers that can reproduce a live MRIQC run and a live
  fMRIPrep-family preprocessing run without downloading data implicitly inside the benchmark script;
- checked-in Phase 2 benchmark metadata, manifests, reports, and provenance notes for at least one
  representative public BIDS fixture or benchmark dataset path;
- runtime evidence for container availability, image references, and harvested upstream outputs;
- status updates that distinguish contract-complete wrappers from scientifically meaningful live
  execution evidence.

Quality gate:
- a reproducible environment demonstrates at least one pinned MRIQC path and one pinned
  fMRIPrep-family path with preserved reports and methods boilerplate;
- benchmark notes stay explicit about what the Phase 2 evidence proves and do not claim scientific
  superiority, clinical validity, or downstream analysis readiness;
- container/runtime availability is demonstrated by commands, not assumed;
- benchmark implications are documented explicitly in checked-in artifacts and status files.

## Priority Order

1. keep the editable-install Python 3.11+ path green locally and in CI
2. keep the checked-in M3 benchmark evidence reproducible and parseable
3. keep `mriqc_report` and `anat_bold_prep` explicit wrappers, not hidden orchestration logic
4. turn Phase 2 wrappers from contract-complete baselines into evidence-backed live benchmark paths
5. defer Phase 3 and diffusion work until Phase 2 live evidence is in place or formally blocked

## Defaults

- keep top-level `skills/<name>/` for contracts, examples, and fixtures;
- keep importable runtime code in `src/clawneuro/skills/<name>/`;
- do not bypass manifests or provenance helpers inside skills;
- do not claim scientific completion when a run is only planned or partial;
- prefer checked-in fidelity fixtures and benchmark notes over invented tool output;
- keep benchmark drivers local-first: require an explicit `--dataset-root` and never auto-download
  private or unpublished user data;
- treat repository-prep for M5 and live evidence generation as separate acceptance layers when the
  runtime environment is unavailable;
- treat local pinned-runtime proof and container proof as complementary, with local proof sufficient
  for the completed M3 milestone.
