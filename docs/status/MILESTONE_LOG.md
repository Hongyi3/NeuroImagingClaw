# Milestone Log

- Status date: March 8, 2026
- Recording rule: entries are added only when milestone completion can be supported by concrete
  repository artifacts. Exact historical completion dates are not invented; this log records what
  is observable by inspection.

## M0 — Documentation and Governance Baseline

- Completion status: observed complete as of March 7, 2026
- Supporting artifacts:
  - `AGENTS.md`
  - `docs/PROJECT-CHARTER.md`
  - `docs/ARCHITECTURE.md`
  - `docs/STANDARDS-MATRIX.md`
  - `docs/ROADMAP.md`
  - `docs/BENCHMARK-SPEC.md`
  - `docs/METHODS-POLICY.md`
  - `docs/DATA-PRIVACY-POLICY.md`
  - `docs/REPRODUCIBILITY-POLICY.md`
  - `docs/IMPLEMENTATION-PLAN.md`
  - `docs/RISK-REGISTER.md`
  - `docs/TEST-STRATEGY.md`
  - `prompts/CODEX_MASTER_PROMPT.md`
  - `docs/status/README.md`
- Verification references:
  - March 7, 2026 repository inspection confirmed the governance and policy corpus is present and
    readable.

## M1 — Shared Foundation

- Completion status: observed complete as of March 7, 2026
- Supporting artifacts:
  - `src/clawneuro/core/bids.py`
  - `src/clawneuro/core/config.py`
  - `src/clawneuro/core/execution.py`
  - `src/clawneuro/core/layout.py`
  - `src/clawneuro/core/models.py`
  - `src/clawneuro/provenance/bundle.py`
  - `src/clawneuro/reporting/models.py`
  - `src/clawneuro/reporting/renderers.py`
  - `src/clawneuro/orchestrator/models.py`
  - `src/clawneuro/cli/app.py`
- Verification references:
  - `tests/test_core_config.py`
  - `tests/test_core_execution.py`
  - `tests/test_core_layout.py`
  - `tests/test_provenance.py`
  - `tests/test_reporting.py`
  - `tests/test_orchestrator.py`
  - `tests/test_cli.py`

## M2 — Phase 1 Skill Contract Layer

- Completion status: observed complete as of March 7, 2026 at prototype and dry-run level
- Supporting artifacts:
  - `src/clawneuro/skills/bids_auditor/runner.py`
  - `src/clawneuro/skills/dicom_to_bids/runner.py`
  - `src/clawneuro/skills/deid_check/runner.py`
  - `skills/bids_auditor/SKILL.md`
  - `skills/dicom_to_bids/SKILL.md`
  - `skills/deid_check/SKILL.md`
  - `skills/catalog.json`
- Verification references:
  - `tests/test_bids_auditor.py`
  - `tests/test_dicom_to_bids.py`
  - `tests/test_deid_check.py`
  - `tests/test_cli.py`
  - `/tmp/clawneuro-m3-bench/bin/python -m clawneuro.cli plan tests/fixtures/bids/minimal`
    returned a Phase 1 plan on March 7, 2026.

## M3 — Phase 1 Execution Hardening and Exit Validation

- Completion status: observed complete as of March 7, 2026
- Supporting artifacts:
  - `src/clawneuro/core/execution.py`
  - `src/clawneuro/skills/dicom_to_bids/runner.py`
  - `benchmarks/run_phase1_public_dicom_to_bids.py`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/benchmark-metadata.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/manifests/conversion-manifest.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/manifests/run-manifest.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/provenance/commands.sh`
  - `benchmarks/PHASE1_FIDELITY.md`
  - `.github/workflows/python-tests.yml`
  - `docs/status/CURRENT_STAGE.md`
  - `docs/status/NEXT_MILESTONE.md`
  - `docs/status/BLOCKERS.md`
- Verification references:
  - `/tmp/clawneuro-m3-bench/bin/python -m pytest` returned `35 passed in 2.01s`.
  - `/tmp/clawneuro-m3-bench/bin/python benchmarks/run_phase1_public_dicom_to_bids.py --workspace /tmp/clawneuro-m3-work --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih`
    regenerated the checked-in benchmark evidence with `status: "succeeded"`.
  - `tests/test_benchmark_artifacts.py` validates the checked-in benchmark manifests and metadata.

## M4 — Phase 2 Wrapper Baseline

- Completion status: observed complete as of March 7, 2026
- Supporting artifacts:
  - `src/clawneuro/core/execution.py`
  - `src/clawneuro/reporting/harvest.py`
  - `src/clawneuro/skills/mriqc_report/config.py`
  - `src/clawneuro/skills/mriqc_report/runner.py`
  - `src/clawneuro/skills/anat_bold_prep/config.py`
  - `src/clawneuro/skills/anat_bold_prep/runner.py`
  - `src/clawneuro/cli/app.py`
  - `skills/mriqc_report/SKILL.md`
  - `skills/anat_bold_prep/SKILL.md`
  - `skills/catalog.json`
  - `tests/fixtures/bids/anat_bold/`
  - `tests/fixtures/phase2/`
  - `tests/test_mriqc_report.py`
  - `tests/test_anat_bold_prep.py`
  - `tests/test_core_execution.py`
  - `tests/test_cli.py`
  - `docs/status/CURRENT_STAGE.md`
  - `docs/status/NEXT_MILESTONE.md`
  - `docs/status/BLOCKERS.md`
- Verification references:
  - `/tmp/clawneuro-m4/bin/python -m pytest` returned `50 passed in 1.54s`.
  - `/tmp/clawneuro-m4/bin/ruff check src tests` returned `All checks passed!`.
  - `/tmp/clawneuro-m4/bin/python -m clawneuro.cli mriqc-report --bids-root tests/fixtures/bids/anat_bold --output-root /tmp/clawneuro-m4-smoke/mriqc --participant-label 01 --modality anat --modality bold --run-group`
    returned a manifest-backed planned QC result with explicit participant and group commands.
  - `/tmp/clawneuro-m4/bin/python -m clawneuro.cli anat-bold-prep --bids-root tests/fixtures/bids/anat_bold --output-root /tmp/clawneuro-m4-smoke/prep --participant-label 01 --output-space MNI152NLin2009cAsym:res-2`
    returned a manifest-backed planned preprocessing result with explicit BIDS-derivative layout and boilerplate/tracking flags.

## Active Milestone Note

- The next active milestone is `M5 — Phase 2 live execution evidence and exit validation for mriqc_report and anat_bold_prep`.
- Repository-prep artifacts for M5 now exist in:
  - `benchmarks/phase2_common.py`
  - `benchmarks/run_phase2_public_mriqc.py`
  - `benchmarks/run_phase2_public_anat_bold_prep.py`
  - `benchmarks/PHASE2_QC_PREP.md`
  - `src/clawneuro/core/execution.py`
  - `src/clawneuro/skills/mriqc_report/runner.py`
  - `src/clawneuro/skills/anat_bold_prep/runner.py`
  - `tests/test_core_execution.py`
  - `tests/test_mriqc_report.py`
  - `tests/test_anat_bold_prep.py`
  - `tests/test_benchmark_artifacts.py`
  - `tests/test_provenance.py`
- `/tmp/clawneuro-m5-full/bin/python -m pytest` returned `59 passed in 2.52s` and
  `/tmp/clawneuro-m5-full/bin/ruff check src tests benchmarks` returned `All checks passed!` on
  March 8, 2026 for the repository-prep state.
- `docs/status/BLOCKERS.md` still records the runtime-availability and dataset-availability
  blockers for that milestone in the inspected workspace, so M5 is not yet logged as complete.
- As of March 8, 2026, the M5 repository-prep layer also pins the real public `ds003020` contract
  through:
  - `benchmarks/phase2_common.py`
  - `benchmarks/run_phase2_public_mriqc.py`
  - `benchmarks/run_phase2_public_anat_bold_prep.py`
  - `benchmarks/PHASE2_QC_PREP.md`
  - `tests/test_benchmark_artifacts.py`
  - `.github/workflows/phase2-live-benchmarks.yml`
- Those files freeze the dataset DOI `doi:10.18112/openneuro.ds003020.v3.1.0`, source commit
  `f74eb2bc95b827d359de338f9086743824d2d906`, and the practical `sub-UTS01/ses-1` subset needed
  for the first live MRIQC and anat/BOLD preprocessing evidence pass.
