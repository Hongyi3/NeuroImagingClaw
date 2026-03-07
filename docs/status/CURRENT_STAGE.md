# Current Stage

- Status date: March 7, 2026
- Roadmap position: **Phase 2 — QC and preprocessing** (`docs/ROADMAP.md`)
- Implementation-plan position: **M5 active; repository-prep landed, live evidence still blocked** (`docs/IMPLEMENTATION-PLAN.md`)
- Implementation-sequence position: Sprint 5 remains the active boundary in
  `prompts/CODEX_IMPLEMENTATION_SEQUENCE.md`
- Default execution target: `docs/status/NEXT_MILESTONE.md`

## Repository Evidence

- Governance and operating documents remain present in `AGENTS.md`, `docs/PROJECT-CHARTER.md`,
  `docs/ARCHITECTURE.md`, `docs/STANDARDS-MATRIX.md`, `docs/ROADMAP.md`,
  `docs/BENCHMARK-SPEC.md`, `docs/METHODS-POLICY.md`, `docs/DATA-PRIVACY-POLICY.md`,
  `docs/REPRODUCIBILITY-POLICY.md`, `docs/IMPLEMENTATION-PLAN.md`, `docs/RISK-REGISTER.md`, and
  `docs/TEST-STRATEGY.md`.
- Shared execution hardening now includes canonical BIDS-App mount helpers for input, output, work,
  config, license, and reuse-derivative paths plus explicit container runtime/image provenance
  capture helpers in `src/clawneuro/core/execution.py`.
- Upstream report and boilerplate harvesting helpers now exist in
  `src/clawneuro/reporting/harvest.py` and are exported through `src/clawneuro/reporting/__init__.py`.
- `mriqc_report` now has a runtime package with typed config, explicit participant/group request
  builders, manifest-backed summary output, and preserved report/IQM harvesting in
  `src/clawneuro/skills/mriqc_report/config.py`,
  `src/clawneuro/skills/mriqc_report/runner.py`, and
  `skills/mriqc_report/SKILL.md`.
- `anat_bold_prep` now has a runtime package with typed config, explicit fMRIPrep-family request
  planning, preserved boilerplate/confounds harvesting, and manifest-backed summary output in
  `src/clawneuro/skills/anat_bold_prep/config.py`,
  `src/clawneuro/skills/anat_bold_prep/runner.py`, and
  `skills/anat_bold_prep/SKILL.md`.
- The public surface now exposes both Phase 2 wrappers in `src/clawneuro/skills/__init__.py`,
  `src/clawneuro/cli/app.py`, `README.md`, and `skills/catalog.json`, with catalog status advanced
  from `planned` to `prototype`.
- Synthetic Phase 2 fixtures now exist in `tests/fixtures/bids/anat_bold/` and
  `tests/fixtures/phase2/`, and the default suite now covers the new wrappers in
  `tests/test_mriqc_report.py`, `tests/test_anat_bold_prep.py`, `tests/test_cli.py`,
  `tests/test_core_execution.py`, and `tests/test_orchestrator.py`.
- The repository now contains the M5 public benchmark harness in `benchmarks/phase2_common.py`,
  `benchmarks/run_phase2_public_mriqc.py`, `benchmarks/run_phase2_public_anat_bold_prep.py`, and
  `benchmarks/PHASE2_QC_PREP.md`.
- The default suite now covers container-provenance downgrade behavior and benchmark-helper
  metadata parsing in `tests/test_core_execution.py`, `tests/test_mriqc_report.py`,
  `tests/test_anat_bold_prep.py`, `tests/test_benchmark_artifacts.py`, and
  `tests/test_provenance.py`.

## Verified Commands

The following commands were verified on March 7, 2026 in a clean `python3.14` virtual environment:

- `python3.14 -m venv /tmp/clawneuro-plan && /tmp/clawneuro-plan/bin/pip install -e '.[dev]'`
  succeeded for the repository-prep verification path.
- `/tmp/clawneuro-plan/bin/python -m pytest` returned `57 passed in 1.53s`.
- `/tmp/clawneuro-plan/bin/ruff check src tests benchmarks` returned `All checks passed!`.
- `/tmp/clawneuro-plan/bin/python benchmarks/run_phase2_public_mriqc.py --help` rendered the
  expected `--dataset-root`, `--workspace`, `--artifact-root`, and `--backend` contract.
- `/tmp/clawneuro-plan/bin/python benchmarks/run_phase2_public_anat_bold_prep.py --help` rendered
  the expected `--dataset-root`, `--workspace`, `--artifact-root`, and `--backend` contract.

## Why the Repository Has Advanced

- The M4 exit criteria recorded in `docs/IMPLEMENTATION-PLAN.md` are now satisfied at contract level.
- `mriqc_report` and `anat_bold_prep` now exist as runtime packages under `src/clawneuro/skills/`,
  not only as skill stubs.
- Each Phase 2 wrapper now defines typed input, output, provenance, and failure contracts and keeps
  upstream report/boilerplate locations explicit in machine-readable manifests.
- The default suite now covers request-shape rendering, harvested artifact preservation,
  `planned` versus `partial` wrapper behavior for Phase 2, and container-provenance downgrade
  behavior when live runtime evidence is incomplete.
- The M5 benchmark harness and protocol note are now present in-repository, so the remaining gap is
  no longer driver implementation; it is execution of those drivers in a container-capable
  environment with public `ds003020`.

## Remaining Repository Reality

- No live Phase 2 benchmark artifacts are checked in yet; the current proof is repository-prep and
  contract-level rather than benchmark-level.
- `docker`, `apptainer`, `mriqc`, and `fmriprep` are all absent in the inspected workspace, so live
  Phase 2 execution evidence is blocked locally and tracked in `docs/status/BLOCKERS.md`.
- No local `ds003020` dataset root exists in the inspected workspace, so the benchmark target is not
  presently runnable here even after the driver scripts were added.
- Phase 3 skills (`task_glm`, `rest_connectivity`, `report_bundle`, `repro_bundle`) and Phase 4
  diffusion work remain unimplemented at runtime level.
