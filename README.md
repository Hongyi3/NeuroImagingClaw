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
- a Typer CLI for planning, audit, intake, QC, preprocessing, and bundle generation;
- importable runtime packages for `bids_auditor`, `dicom_to_bids`, `deid_check`, `mriqc_report`,
  and `anat_bold_prep`;
- deterministic reporting, reproducibility, and upstream-artifact harvesting helpers;
- contract/unit/integration tests with synthetic Phase 1 and Phase 2 fixtures;
- pinned Phase 1 fidelity fixtures and checked-in public benchmark artifacts for BIDS Validator and
  `dcm_qa_nih` DICOM-to-BIDS conversion.

Phase 1 is evidence-backed and complete at the repository level. Phase 2 now has contract-complete
wrapper baselines for MRIQC and fMRIPrep-style preprocessing, and the repository is being prepared
for Docker-first live benchmark evidence on public `ds003020`. In this inspected workspace,
however, `docker`, `apptainer`, `mriqc`, and `fmriprep` are all absent, so Phase 2 live evidence is
still blocked on the execution environment rather than the wrapper contracts.

## Verified developer path

ClawNeuro expects Python 3.11+. The supported developer loop is:

```bash
python3.11+ -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m clawneuro.cli plan tests/fixtures/bids/minimal
```

The verified local path in this workspace used the same steps under `python3.14`. The checked-out
`.venv` currently targets Python 3.9 and should not be treated as a supported verification
environment for this repository.

## Public benchmark path

The checked-in Phase 1 public-case evidence was generated with:

```bash
python3.14 -m venv /tmp/clawneuro-m3
/tmp/clawneuro-m3/bin/pip install -e '.[dev]' dcm2bids==3.2.0 dcm2niix==1.0.20250506 bids-validator-deno==2.4.1
/tmp/clawneuro-m3/bin/python benchmarks/run_phase1_public_dicom_to_bids.py --workspace /tmp/clawneuro-m3-work --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih
```

The resulting manifests, reports, logs, and reproducibility bundle are checked in under
`benchmarks/artifacts/phase1_dcm_qa_nih/`.

Phase 2 benchmark drivers are also expected under `benchmarks/`, with public `ds003020`
(`doi:10.18112/openneuro.ds003020.v3.1.0`) as the default target dataset once a container-capable
environment is available. The pinned benchmark subset is `sub-UTS01/ses-1` with one T1w image and
one `task-CategoryLocalizer1_run-1` BOLD run. Those drivers must take an explicit `--dataset-root`;
they do not auto-download data inside the benchmark run.

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
- `src/clawneuro/reporting/harvest.py`: preserved upstream report, IQM, confounds, and boilerplate discovery
- `src/clawneuro/orchestrator/`: planning-only dataset inspection and Phase 1 workflow plans
- `src/clawneuro/skills/`: runtime packages for Phase 1 skills plus `mriqc_report` and `anat_bold_prep`
- `src/clawneuro/cli/`: `plan`, `bids-auditor`, `dicom-to-bids`, `deid-check`, `mriqc-report`,
  `anat-bold-prep`, `report-bundle`, and `repro-bundle`

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
.venv/bin/python -m clawneuro.cli plan /path/to/input

# dry-run BIDS audit
.venv/bin/python -m clawneuro.cli bids-auditor --bids-root /path/to/bids --output-root outputs/bids-audit

# dry-run DICOM conversion planning with an explicit Dcm2Bids config
.venv/bin/python -m clawneuro.cli dicom-to-bids \
  --source-root /path/to/dicom \
  --output-root outputs/dicom-to-bids \
  --participant-label ID01 \
  --curation-config-path /path/to/dcm2bids_config.json

# local de-identification readiness assessment
.venv/bin/python -m clawneuro.cli deid-check --bids-root /path/to/bids --output-root outputs/deid-check

# dry-run MRIQC wrapper planning with explicit participant and modality filters
.venv/bin/python -m clawneuro.cli mriqc-report \
  --bids-root /path/to/bids \
  --output-root outputs/mriqc \
  --participant-label 01 \
  --modality anat \
  --modality bold \
  --run-group

# dry-run anat + BOLD preprocessing planning with explicit BIDS-derivative output layout
.venv/bin/python -m clawneuro.cli anat-bold-prep \
  --bids-root /path/to/bids \
  --output-root outputs/prep \
  --participant-label 01 \
  --output-space MNI152NLin2009cAsym:res-2

# rerun the pinned public Phase 1 benchmark
.venv/bin/python benchmarks/run_phase1_public_dicom_to_bids.py \
  --workspace /tmp/clawneuro-m3-work \
  --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih
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
