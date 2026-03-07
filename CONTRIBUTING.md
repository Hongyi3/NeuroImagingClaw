# Contributing to ClawNeuro

Thank you for contributing. ClawNeuro aims to be scientific infrastructure, not a loose collection
of prompts and wrappers, so contributions are reviewed for methodological rigor as well as code quality.

## Before opening a PR

Please read:

- `docs/PROJECT-CHARTER.md`
- `docs/ARCHITECTURE.md`
- `docs/METHODS-POLICY.md`
- `docs/REPRODUCIBILITY-POLICY.md`
- `AGENTS.md`

## Contribution categories

- bug fixes;
- new skills;
- benchmark additions;
- report or provenance improvements;
- documentation improvements;
- community and governance improvements.

## Required for all substantive PRs

- tests;
- documentation updates;
- an explicit statement of whether benchmark behavior changed;
- example or fixture updates if outputs changed;
- no breaking change to output contracts without a versioned migration note.

## Skill contribution rules

Each new skill must include:

- `SKILL.md`;
- a clear execution contract;
- sample inputs or fixtures;
- expected outputs;
- provenance behavior;
- failure-mode documentation;
- at least one integration path in `skills/catalog.json`.

## Review questions used by maintainers

- Does this preserve BIDS compatibility?
- Does this preserve provenance?
- Does this wrap an existing trusted tool when appropriate?
- Does this keep task and rest analysis pathways conceptually separate?
- Does the report avoid unsupported scientific claims?
- Can an external lab understand and rerun the feature?

## Community process

Use GitHub issues for roadmap and bugs. Use public neuroimaging community spaces for general workflow
questions whenever possible, so answers remain searchable and reusable.
