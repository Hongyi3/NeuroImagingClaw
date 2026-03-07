# AGENTS.md

This repository is intentionally designed for both human contributors and AI coding agents.
If you are an agent working here, follow these rules.

## Primary objective

Build **ClawNeuro**, a BIDS-native neuroimaging orchestration layer modeled after ClawBio’s
modular-skill architecture. Your job is to implement trustworthy infrastructure, not to produce
flashy demos at the expense of scientific rigor.

## Non-negotiable constraints

1. **Do not replace established neuroimaging tools.**
   Wrap and standardize trusted components such as dcm2niix, HeuDiConv/Dcm2Bids, the BIDS
   Validator, MRIQC, fMRIPrep, FitLins/Nilearn, XCP-D, QSIPrep, QSIRecon, TemplateFlow, and
   DataLad.

2. **Do not bypass BIDS.**
   Inputs, intermediate reasoning, and outputs should stay as close as possible to BIDS and BIDS
   Derivatives. Custom side outputs are allowed only when they are clearly auxiliary.

3. **Do not treat task fMRI and resting-state as the same downstream workflow.**
   Task GLM and connectivity post-processing must split after preprocessing.

4. **Do not let the language model invent scientific results.**
   The LLM may route, summarize, explain, draft, and assemble. Quantitative claims must come from
   tool outputs, metadata, or benchmark evidence.

5. **Do not mark a run complete without provenance.**
   Every run must emit exact commands, versions, hashes, logs, and machine-readable manifests.

6. **Do not add cloud upload or external data transfer by default.**
   Default behavior is local-first. Any upload or network egress touching user data must be
   explicit and documented.

7. **Do not make clinical claims.**
   The platform is research-use-only.

## Read these files before coding

- `docs/PROJECT-CHARTER.md`
- `docs/ARCHITECTURE.md`
- `docs/STANDARDS-MATRIX.md`
- `docs/ROADMAP.md`
- `docs/BENCHMARK-SPEC.md`
- `docs/METHODS-POLICY.md`
- `docs/DATA-PRIVACY-POLICY.md`
- `docs/REPRODUCIBILITY-POLICY.md`
- `prompts/CODEX_MASTER_PROMPT.md`

## Expected implementation style

- Use small, auditable modules.
- Keep execution contracts explicit.
- Favor typed configuration objects over freeform dictionaries.
- Put all user-visible science into reports or JSON manifests that can be traced back to a run.
- Preserve upstream visual reports where possible; do not overwrite or hide them.
- Write tests before claiming milestone completion.
- Keep documentation current as code changes.

## Architecture invariants

- Each skill must work standalone and through the orchestrator.
- The orchestrator may plan and chain skills, but it must not perform science that belongs inside a skill.
- All derivative directories must be BIDS-compliant when claimed as BIDS Derivatives.
- Every skill must define its input contract, output contract, provenance contract, and failure modes.
- Report generation must be deterministic given the same executed workflow metadata.

## Required artifacts per meaningful feature PR

- code;
- tests;
- docs update;
- example output or fixture;
- provenance notes;
- benchmark note if behavior affects scientific outputs.

## If you need to deviate

If the best implementation appears to conflict with this repository’s constitution:

1. stop;
2. create an ADR-style note in `docs/`;
3. explain the trade-off;
4. do not silently diverge.
