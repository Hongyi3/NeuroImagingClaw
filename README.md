# ClawNeuro

ClawNeuro is a BIDS-native neuroimaging orchestration layer focused on auditable infrastructure:
typed contracts, reproducibility artifacts, deterministic reporting, and narrow wrappers around
trusted upstream tools.

## Positioning

ClawNeuro should be:

- **BIDS-native** rather than ad hoc.
- **Glass-box** rather than black-box.
- **Local-first** and privacy-preserving by default.
- **Derivative-first** and publication-ready.
- **Wrapper-first** around trusted neuroimaging tools rather than a reinvention of them.
- **Research-use-only** for the foreseeable roadmap.

ClawNeuro should **not** be:

- a new preprocessing suite competing with fMRIPrep, MRIQC, QSIPrep, or XCP-D;
- a freeform prompt layer that invents preprocessing choices;
- a clinical decision system;
- a platform that emits custom output layouts when BIDS Derivatives already solves the problem.

## Current repository state

The repository now contains:

- governing project documents and policies;
- a typed shared core for manifests, configs, execution plans, and provenance;
- a Typer CLI for planning, audit, intake, and bundle generation;
- importable runtime packages for `bids_auditor`, `dicom_to_bids`, and `deid_check`;
- deterministic reporting and reproducibility helpers;
- contract/unit/integration tests with synthetic Phase 1 fixtures.

This is still an early foundation release. Heavy upstream execution paths such as MRIQC, fMRIPrep,
XCP-D, and QSIPrep are not implemented yet.

## Reading order for a coding agent

1. `docs/PROJECT-CHARTER.md`
2. `docs/ARCHITECTURE.md`
3. `docs/STANDARDS-MATRIX.md`
4. `docs/ROADMAP.md`
5. `docs/BENCHMARK-SPEC.md`
6. `docs/METHODS-POLICY.md`
7. `docs/DATA-PRIVACY-POLICY.md`
8. `docs/REPRODUCIBILITY-POLICY.md`
9. `prompts/CODEX_MASTER_PROMPT.md`
10. `skills/catalog.json`

## Implemented foundation surface

- `src/clawneuro/core/`: typed contracts, config loading, BIDS helpers, execution planning, layout
- `src/clawneuro/provenance/`: checksums, environment snapshots, manifest writing
- `src/clawneuro/reporting/`: deterministic methods text and markdown bundle assembly
- `src/clawneuro/orchestrator/`: planning-only dataset inspection and Phase 1 workflow plans
- `src/clawneuro/skills/`: runtime packages for Phase 1 intake/audit/privacy skills
- `src/clawneuro/cli/`: `plan`, `bids-auditor`, `dicom-to-bids`, `deid-check`, `report-bundle`,
  and `repro-bundle`

## Implementation order

1. Foundation and governance
2. Shared core types and run manifests
3. `bids_auditor`
4. `dicom_to_bids`
5. `deid_check`
6. `mriqc_report`
7. `anat_bold_prep`
8. split downstream path into `task_glm` and `rest_connectivity`
9. `report_bundle`
10. `repro_bundle`
11. `diffusion_prep`
12. benchmark hardening and paper artifacts

## Usage

```bash
# inspect and plan a Phase 1 workflow
python3 -m clawneuro.cli plan /path/to/input

# dry-run BIDS audit
python3 -m clawneuro.cli bids-auditor --bids-root /path/to/bids --output-root outputs/bids-audit

# dry-run DICOM conversion planning
python3 -m clawneuro.cli dicom-to-bids --source-root /path/to/dicom --output-root outputs/dicom-to-bids

# local de-identification readiness assessment
python3 -m clawneuro.cli deid-check --bids-root /path/to/bids --output-root outputs/deid-check
```

## Definition of success

A new lab should be able to point ClawNeuro at a DICOM directory or a valid BIDS dataset and
receive:

- BIDS validation status,
- de-identification readiness status,
- QC reports,
- BIDS-compliant derivatives,
- machine-readable provenance,
- manuscript-ready methods text,
- a reproducibility bundle,
- and a citable open-source release.

## Important implementation rule

If a design decision would conflict with BIDS, NiPreps conventions, OpenNeuro upload rules, or
the explicit contracts in this repository, the repository contracts win and the implementation
must be changed rather than silently improvising.
