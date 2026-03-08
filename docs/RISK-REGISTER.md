# Risk Register

## Current top risks

| ID | Risk | Impact | Current status | Mitigation |
|---|---|---|---|---|
| R1 | Runtime provenance completeness could regress if wrapped tools change their version-reporting behavior | A future live run could fall back from `succeeded` to `partial` even when execution completes | Open | Keep `src/clawneuro/core/execution.py`, `src/clawneuro/skills/dicom_to_bids/runner.py`, and `tests/test_core_execution.py` aligned with observed upstream version output |
| R2 | Checked-in public benchmark artifacts are snapshots, not the raw benchmark dataset | Evidence remains reproducible, but the repository still depends on network fetch at benchmark time | Open | Preserve `benchmarks/run_phase1_public_dicom_to_bids.py`, `benchmarks/artifacts/phase1_dcm_qa_nih/`, and archive SHA256 metadata together |
| R3 | Docker and Apptainer are absent in the inspected workspace, and MRIQC/fMRIPrep are not installed locally | Phase 2 live execution evidence is blocked in this workspace even though request planning and wrapper contracts are implemented | Open | Keep contract coverage green, record the blocker in `docs/status/BLOCKERS.md`, and verify pinned Phase 2 runs in a container-capable environment |

## Implementation risks

| ID | Risk | Impact | Current status | Mitigation |
|---|---|---|---|---|
| R4 | `dicom_to_bids` now synthesizes a minimum `dataset_description.json` when upstream curation omits it | This preserves validator success, but the synthesized dataset name still needs human review before publication-facing release | Open | Keep the synthesis explicit in manifests, reports, warnings, and the skill contract |
| R5 | `dicom_to_bids` removes upstream `tmp_dcm2bids` from the curated output before validation | This improves BIDS validity, but upstream temp contents are no longer present inside the dataset tree | Open | Preserve the wrapped command logs and document the cleanup behavior as internal execution hygiene |
| R6 | Privacy checks rely on conservative filename and sidecar inspection | False negatives are safer than false positives, but usability may suffer | Open | Keep rule IDs and policy references explicit, and expand only with metadata-backed criteria |
| R7 | Report and methods generation remain early even when deterministic | Publication-facing phrasing may still need methods review | Open | Review methods templates alongside benchmark evidence and future Phase 2 report harvesting |
| R8 | Placeholder org metadata remains in public-facing files | Repository presentation is not publication-ready | Open | Replace `YOUR-ORG` placeholders in `CITATION.cff`, `CODEOWNERS`, skill headers, and templates |
| R9 | MRIQC telemetry suppression (`--no-sub`) and fMRIPrep tracking suppression (`--notrack`) are user-overridable | The default privacy posture could drift if callers disable those flags without documenting why | Open | Keep both defaults enabled in config models and surface warnings when users disable them |
| R10 | FreeSurfer-enabled preprocessing requires an external license file and environment-specific availability | Live `anat_bold_prep` coverage can fail or diverge across environments when FreeSurfer is enabled | Open | Keep license requirements explicit in `AnatBoldPrepConfig`, test the guarded path, and defer live FreeSurfer claims until a reproducible environment is available |
| R11 | Phase 2 wrapper verification currently relies on synthetic output-harvest fixtures, not executed upstream MRIQC/fMRIPrep runs | M4 proves the wrapper contracts, but not yet the scientific/runtime fidelity of live Phase 2 execution | Open | Treat M5 live execution evidence as required follow-on work before claiming Phase 2 exit readiness |
| R12 | The checked-out `.venv` uses Python 3.9 while the repository requires Python 3.11+ | Developers can misread interpreter failures as contract regressions instead of unsupported-environment failures | Open | Document and verify the supported Python 3.11+/3.14 path explicitly in `README.md`, `docs/TEST-STRATEGY.md`, and status updates |
| R13 | Phase 2 benchmark drivers may exist before a container-capable environment is available | The repository can be operationally ready for M5 while still lacking honest checked-in live evidence | Open | Keep benchmark drivers, docs, and tests ready around the pinned `ds003020` DOI `doi:10.18112/openneuro.ds003020.v3.1.0` `sub-UTS01/ses-1` subset, but do not claim M5 completion until real Docker or Apptainer artifacts are checked in |

## Release gates tied to this register

- Do not claim Phase 2 live execution evidence until R3 and R11 are retired in at least one
  reproducible environment.
- Do not claim Phase 2 milestone completion while R13 remains open, even if the benchmark harness
  and status files are otherwise ready.
- Do not claim OpenNeuro-readiness automation beyond technical checks while R6 remains open.
- Do not claim publication-ready repository hygiene while R8 remains open.
