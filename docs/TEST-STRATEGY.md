# Test Strategy

## Summary

Testing should prove contract stability first, wrapped-tool fidelity second, and heavy public
benchmark execution only through pinned, reproducible paths. The default suite stays lightweight by
using fixtures, stub executables, synthetic Phase 2 harvest trees, and checked-in benchmark
artifacts, while opt-in benchmark execution reproduces public workflows when the required runtimes
are present.

## Default developer path

Use an editable install under Python 3.11+:

```bash
python3.11+ -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m clawneuro.cli plan tests/fixtures/bids/minimal
```

Local M4 verification in this workspace used the same path under `python3.14`.

The checked-out `.venv` currently targets Python 3.9 and should not be used as the repository's
verification environment.

## Test matrix

### Default suite: fast and local

Targets:
- core models and enum validation
- config loading from YAML/JSON/TOML
- local, Docker, and Apptainer request rendering
- executable resolution, PATH augmentation, and version probing
- run-directory layout helpers
- provenance checksum and manifest writing
- deterministic reporting and methods rendering
- orchestration planning logic
- contract tests for `bids_auditor`, `dicom_to_bids`, `deid_check`, `mriqc_report`, and `anat_bold_prep`
- CLI integration tests against synthetic fixtures, dry-run skill execution, and config-file loading
- validation that checked-in benchmark artifacts still parse and report `succeeded`

Goal:
- prove that ClawNeuro’s internal contracts stay typed, stable, and deterministic without requiring
  heavyweight neuroimaging runtimes in the routine developer loop.

### Stubbed live-execution contract tests

Targets:
- `dicom_to_bids` execute-path tests using stub `dcm2bids`, `dcm2niix`, and
  `bids-validator-deno` executables
- `mriqc_report` execute-path tests using synthetic output harvest fixtures plus monkeypatched
  command execution
- `anat_bold_prep` execute-path tests using synthetic output harvest fixtures plus monkeypatched
  command execution

Assertions:
- local PATH augmentation from `dcm2niix_executable` works when an explicit path is supplied
- runtime evidence captures resolved executables and version strings
- live conversion returns `succeeded` only when execution and provenance proof are both complete
- live conversion returns `partial` when execution succeeds but runtime provenance is incomplete
- MRIQC returns `succeeded` only when reports, IQM tables, and derivative metadata are harvested
- preprocessing returns `partial` when reports, boilerplate, or derivative metadata are missing

Goal:
- keep execute-path logic covered without turning the default suite into a heavyweight benchmark.

### Opt-in public benchmark execution

Targets:
- `benchmarks/run_phase1_public_dicom_to_bids.py`
- `benchmarks/artifacts/phase1_dcm_qa_nih/`

Verification path:

```bash
python3.14 -m venv /tmp/clawneuro-m3
/tmp/clawneuro-m3/bin/pip install -e '.[dev]' dcm2bids==3.2.0 dcm2niix==1.0.20250506 bids-validator-deno==2.4.1
/tmp/clawneuro-m3/bin/python benchmarks/run_phase1_public_dicom_to_bids.py --workspace /tmp/clawneuro-m3-work --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih
```

Goal:
- reproduce the checked-in public Phase 1 evidence with pinned local runtimes and exact provenance.

### Prepared Phase 2 benchmark path

Targets:
- `mriqc_report`
- `anat_bold_prep`
- `benchmarks/run_phase2_public_mriqc.py`
- `benchmarks/run_phase2_public_anat_bold_prep.py`
- Docker-first live execution with Apptainer fallback on public `ds003020`

Goal:
- prove that QC and preprocessing wrappers preserve upstream reports, boilerplate, and container
  provenance in a real runtime environment, not only through synthetic fixtures.

Verification path once the runtime blocker is cleared:

```bash
python3.14 -m venv /tmp/clawneuro-m5
/tmp/clawneuro-m5/bin/pip install -e '.[dev]'
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_mriqc.py --dataset-root <ds003020_root> --workspace /tmp/clawneuro-m5-work/mriqc --artifact-root benchmarks/artifacts/phase2_ds003020_mriqc
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_anat_bold_prep.py --dataset-root <ds003020_root> --workspace /tmp/clawneuro-m5-work/prep --artifact-root benchmarks/artifacts/phase2_ds003020_anat_bold_prep
```

## Fixture policy

- keep default fixtures local, synthetic, and small;
- keep small public-case fidelity excerpts under `tests/fixtures/fidelity/` when they are needed to
  prove wrapper compatibility;
- keep checked-in benchmark evidence limited to manifests, reports, logs, and metadata rather than
  raw benchmark datasets;
- prefer filename/metadata fixtures over bulky imaging payloads for contract tests;
- never substitute smoke fixtures for scientific benchmark evidence.

## Quality gates

- new shared-core behavior requires unit tests;
- new or changed skill contracts require contract tests and fixture updates;
- output-contract changes require docs updates in the same patch;
- benchmark-affecting behavior requires a benchmark note or checked-in artifact rationale;
- public benchmark execution stays opt-in, but its checked-in artifacts must remain parseable in the
  default suite;
- while live Phase 2 artifacts are still blocked, benchmark-driver metadata and provenance helpers
  must still be covered in the default suite so the repository stays ready for the eventual live
  run;
- status-file changes are part of the acceptance criteria for milestone work.
