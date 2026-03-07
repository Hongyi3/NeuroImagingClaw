# Risk Register

## Active blockers

| ID | Risk | Impact | Current status | Mitigation |
|---|---|---|---|---|
| R1 | Local environment is Python 3.9.13 while `pyproject.toml` requires Python 3.11+ | Full validation of the declared runtime contract is blocked in this workspace | Open | Move test and lint execution to Python 3.11 before claiming release readiness |
| R2 | External toolchain is not installed locally (`bids-validator`, `dcm2niix`, `dcm2bids`/`heudiconv`, Docker/Apptainer, MRIQC, fMRIPrep, XCP-D, QSIPrep, DataLad) | Wrapped execution paths cannot be verified end-to-end here | Open | Keep dry-run planning explicit; add pinned tool/container installs in controlled environments |
| R3 | Workspace is not initialized as a Git repository | Git-based provenance and release checks cannot run | Open | Initialize Git before release engineering, benchmark freezing, or contributor workflow validation |

## Implementation risks

| ID | Risk | Impact | Current status | Mitigation |
|---|---|---|---|---|
| R4 | Synthetic fixtures are lighter than real public benchmark data | Phase 1 tests may miss validator/schema/tool edge cases | Open | Add opt-in smoke datasets and frozen public benchmark subsets before milestone promotion |
| R5 | DICOM conversion wrappers currently rely on planned command generation more than validated tool execution | Contract shape may drift from upstream CLI behavior if not checked early | Open | Test planned argv against pinned upstream versions and container interfaces |
| R6 | Privacy checks rely on conservative filename and sidecar inspection | False negatives are safer than false positives, but usability may suffer | Open | Document the conservative rule set and expand with explicit metadata-backed criteria only |
| R7 | Report and methods generation are deterministic but early | Publication-facing phrasing may need further methods review even when traceable | Open | Review methods templates alongside benchmark evidence and upstream boilerplate integration |
| R8 | Placeholder org metadata remains in public-facing files | Repository presentation is not publication-ready | Open | Replace `YOUR-ORG` placeholders in `CITATION.cff`, `CODEOWNERS`, skill headers, and templates |

## Release gates tied to this register

- Do not claim a release-quality Phase 1 milestone until R1 and R2 are retired in at least one
  reproducible environment.
- Do not claim OpenNeuro-readiness automation beyond technical checks while R6 remains open.
- Do not claim publication-ready repository hygiene while R8 remains open.
