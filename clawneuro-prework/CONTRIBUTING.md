# Contributing to ClawNeuro

Thank you for contributing.

## Project philosophy

ClawNeuro is infrastructure for reproducible computational neuroscience. Contributions should improve:
- standards adoption,
- benchmark coverage,
- reproducibility,
- interoperability,
- documentation quality.

## Contribution types

We welcome:
- new skills
- benchmark fixtures and manifests
- docs improvements
- bug fixes
- validator integration
- reproducibility tooling
- container and CI improvements

## Before you code

Read:
1. `AGENTS.md`
2. `PROJECT_PLAN.md`
3. `docs/architecture.md`
4. `templates/SKILL-TEMPLATE.md`

## Adding a new skill

```bash
mkdir -p skills/your-skill-name
cp templates/SKILL-TEMPLATE.md skills/your-skill-name/SKILL.md
```

Then add:
```text
skills/your-skill-name/
├── SKILL.md
├── examples/
├── tests/
└── your_skill.py   # optional at first, expected for production skills
```

## Minimum quality bar

A proposed skill must include:
- complete YAML frontmatter in `SKILL.md`
- clear methodology
- example queries
- output structure
- validator and backend notes
- failure modes
- tests
- demo path
- benchmark entry
- citations / references

For any skill whose `status` is not `planned` or `planned-phase-2`, frontmatter must also include:
- `entrypoint`
- `demo_paths`
- `test_paths`

## Trust tiers

Every skill must declare one of:
- `core`
- `reviewed-community`
- `experimental`

Experimental skills are not routed by default.

## Code standards

- Python 3.11+
- type hints encouraged
- pathlib for paths
- no hardcoded absolute paths
- tests with `pytest`
- keep functions small and explicit
- separate orchestration from scientific kernels

## Required commands

```bash
python clawneuro.py list
python clawneuro.py route --query "Inspect this NWB file" --input examples/synthetic/session_stub.nwb --json
python clawneuro.py demo foundation --output outputs/foundation-demo
python scripts/generate_catalog.py
python scripts/validate_benchmarks.py
python -m pytest -q
```

## Pull requests

Please keep PRs:
- small,
- benchmark-aware,
- documented,
- test-backed.

Each PR should explain:
- what changed
- which milestone it supports
- benchmark impact
- new dependencies
- open risks or follow-up work
