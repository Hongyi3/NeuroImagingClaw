# Tests

Current test coverage focuses on the shared foundation plus Phase 1 and Phase 2 wrapper contracts:

- unit tests for typed manifests, config loading, layout helpers, provenance, and reporting;
- unit tests for local and container execution request rendering, canonical BIDS-App mount helpers,
  and executable/version probing;
- planner tests for dataset inspection and Phase 1 handoff logic;
- contract tests for `bids_auditor`, `dicom_to_bids`, and `deid_check`, including stubbed live
  `dicom_to_bids` execution;
- contract tests for `mriqc_report` and `anat_bold_prep`, including preserved report/boilerplate
  harvesting and `partial` status coverage;
- CLI integration tests against synthetic fixtures and dry-run skill execution, including config-file
  loading for Phase 2 wrappers;
- fidelity tests against pinned public-case validator JSON excerpts;
- artifact validation tests for the checked-in `dcm_qa_nih` benchmark evidence.

Run the supported developer path with:

```bash
python3.11+ -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m clawneuro.cli plan tests/fixtures/bids/minimal
```

Heavy upstream MRIQC/fMRIPrep execution is intentionally not part of the default test suite yet.
Phase 2 live benchmark and container-backed regression coverage remains an opt-in target that
depends on Docker or Apptainer plus a local public `ds003020` dataset root. The pinned Phase 2
target is the `doi:10.18112/openneuro.ds003020.v3.1.0` `sub-UTS01/ses-1` subset with one T1w
image and one `task-CategoryLocalizer1_run-1` BOLD run. The repository-side M5 prep should still
stay covered by unit tests, fixture tests, and benchmark-driver metadata tests in the default
suite.

To rerun the checked-in public benchmark evidence:

```bash
python3.14 -m venv /tmp/clawneuro-m3
/tmp/clawneuro-m3/bin/pip install -e '.[dev]' dcm2bids==3.2.0 dcm2niix==1.0.20250506 bids-validator-deno==2.4.1
/tmp/clawneuro-m3/bin/python benchmarks/run_phase1_public_dicom_to_bids.py --workspace /tmp/clawneuro-m3-work --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih
```

Planned M5 live verification commands once the runtime blocker is cleared:

```bash
python3.14 -m venv /tmp/clawneuro-m5
/tmp/clawneuro-m5/bin/pip install -e '.[dev]'
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_mriqc.py --dataset-root <ds003020_root> --workspace /tmp/clawneuro-m5-work/mriqc --artifact-root benchmarks/artifacts/phase2_ds003020_mriqc --backend docker
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_anat_bold_prep.py --dataset-root <ds003020_root> --workspace /tmp/clawneuro-m5-work/prep --artifact-root benchmarks/artifacts/phase2_ds003020_anat_bold_prep --backend docker
```
