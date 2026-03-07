# Implementation Plan

## Summary

ClawNeuro now has the shared foundation needed for Phase 1 skills: typed manifests, config loading,
execution planning, reproducibility helpers, deterministic reporting primitives, and a planning CLI.
The next work should build outward from those contracts rather than bypassing them.

## Milestones

### M0. Documentation and governance baseline

- maintain `docs/IMPLEMENTATION-PLAN.md`, `docs/RISK-REGISTER.md`, and `docs/TEST-STRATEGY.md` as the
  authoritative execution baseline;
- keep `README.md`, `tests/README.md`, and skill contracts synchronized with implementation status;
- replace remaining placeholder org metadata before public release.

Quality gate:
- docs reflect the actual code surface and known blockers.

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
- canonical run-directory layout and BIDS derivative metadata helpers;
- deterministic methods/report rendering;
- minimum reproducibility bundle writing;
- planning CLI and report/repro bundle entry points.

Quality gate:
- unit tests cover model validation, serialization, layout, reporting, and provenance behavior.

### M2. Phase 1 skills

File targets:
- `src/clawneuro/skills/bids_auditor/`
- `src/clawneuro/skills/dicom_to_bids/`
- `src/clawneuro/skills/deid_check/`
- `skills/bids_auditor/`
- `skills/dicom_to_bids/`
- `skills/deid_check/`

Deliverables:
- `bids_auditor` dry-run and executable validator command planning with normalized summaries;
- `dicom_to_bids` wrapped dcm2niix plus curation command planning with curation manifests;
- `deid_check` conservative shareability assessment with structural-image privacy checks;
- manifest-backed outputs and provenance artifacts for each skill.

Quality gate:
- contract tests cover input validation, output files, warnings, and provenance minimums.

### M3. Upstream execution hardening

Dependencies:
- Python 3.11 runtime
- wrapped tools or container runtimes installed and pinned

Deliverables:
- real tool execution paths for BIDS Validator, dcm2niix, and Dcm2Bids/HeuDiConv in CI-adjacent
  environments;
- pinned container/image capture and version resolution;
- fixture expansion beyond synthetic smoke data.

Quality gate:
- smoke benchmarks are reproducible with exact commands, versions, and checksums.

## Priority order

1. harden foundation tests and Python 3.11 execution
2. validate `bids_auditor` against real BIDS Validator JSON
3. validate `dicom_to_bids` against public DICOM examples
4. refine `deid_check` rules with documented OpenNeuro-facing criteria
5. begin Phase 2 wrappers only after the Phase 1 contract surface is stable

## Defaults

- keep top-level `skills/<name>/` for contracts, examples, and fixtures;
- keep importable runtime code in `src/clawneuro/skills/<name>/`;
- do not bypass manifests or provenance helpers inside skills;
- do not claim scientific completion when a run is only planned.
