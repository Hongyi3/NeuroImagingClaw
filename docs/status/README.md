# Status Control

## Purpose

The `docs/status/` folder is the live operational source of truth for milestone sequencing, current
repository stage, blocker tracking, and Codex-to-human handoff. It exists to make substantial work
deterministic, reviewable, and auditable across sessions.

## Precedence

For live execution order and progress tracking, the files in `docs/status/` govern day-to-day work.
`docs/IMPLEMENTATION-PLAN.md` remains strategic context, and `docs/ROADMAP.md` plus
`prompts/CODEX_IMPLEMENTATION_SEQUENCE.md` remain the high-level sequencing references. None of
these status files override the ClawNeuro constitution in `AGENTS.md`, `docs/PROJECT-CHARTER.md`,
`docs/ARCHITECTURE.md`, `docs/METHODS-POLICY.md`, `docs/DATA-PRIVACY-POLICY.md`, or
`docs/REPRODUCIBILITY-POLICY.md`.

## File Roles

- `CURRENT_STAGE.md`: the repository's actual current stage, backed by concrete repository
  evidence.
- `NEXT_MILESTONE.md`: the default execution target, including milestone mapping, out-of-scope
  work, and exit criteria.
- `BLOCKERS.md`: active blockers for the current milestone, each with evidence, impact, and an
  unblock condition.
- `MILESTONE_LOG.md`: milestones that are completed by evidence, including the repository artifacts
  that support the claim.

## Update Protocol

1. Read all status files before any substantial implementation, documentation, or contract work.
2. Treat `NEXT_MILESTONE.md` as the default target unless the milestone is blocked and recorded in
   `BLOCKERS.md`, or an ADR in `docs/` authorizes resequencing.
3. After each substantial work cycle, update the relevant status files with the concrete repository
   artifacts that changed.
4. Add, retire, or refine blocker entries in `BLOCKERS.md` whenever the current milestone is
   constrained by runtime, tooling, fixture, policy, or sequencing issues.
5. Add an entry to `MILESTONE_LOG.md` only when milestone exit criteria are met and can be cited by
   real files, tests, docs, commands, or manifests.
6. If milestone order must change, create an ADR under `docs/` and cite it from the updated status
   files.

## What Counts as a Substantial Work Cycle

A substantial work cycle is any nontrivial change to code, tests, contracts, CLI behavior,
provenance behavior, benchmark handling, or repository documentation beyond typo-only edits.

## Evidence Standard

Status updates must reference real repository artifacts, including file paths, tests, fixtures,
commands, manifests, logs, docs, contracts, and unresolved issues. Statements such as "almost
done," "mostly complete," or "progressing well" are not acceptable without artifact-backed
evidence.
