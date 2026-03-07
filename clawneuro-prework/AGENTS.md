# AGENTS.md

This repository is designed to be extended by AI coding agents and human contributors.

## Mission

Build **ClawNeuro** into a standards-native, benchmark-first computational neuroscience infrastructure project.

Do **not** turn it into:
- a generic “AI for neuroscience” wrapper,
- an unvalidated notebook zoo,
- a new data standard,
- an ad hoc analysis repo with a chat interface on top.

## Core product rules

1. **Prefer field standards over project-local formats**
   - NWB / DANDI
   - BIDS / OpenNeuro
   - NeuroML / PyNN
   - existing archive metadata and simulator metadata

2. **Prefer orchestration over reimplementation**
   - Wrap mature domain libraries.
   - Do not recreate their algorithms unless there is a compelling scientific reason.

3. **Preserve local-first execution**
   - Public archives may be queried or cached.
   - User data should not require cloud upload.

4. **Make reproducibility an output**
   - Every skill must define the files in its reproducibility bundle.

5. **Benchmark before claiming usefulness**
   - No unbenchmarked skill should become a core routed skill.

## Mandatory reading order for agents

1. `README.md`
2. `PROJECT_PLAN.md`
3. `docs/architecture.md`
4. `docs/codex-implementation-brief.md`
5. `templates/SKILL-TEMPLATE.md`
6. target skill `SKILL.md`
7. `skills/catalog.json`

## Required implementation order

### Milestone 1
- catalog tooling
- orchestrator skeleton
- reproducibility bundle scaffolding
- benchmark manifest validation
- tests and CI

### Milestone 2
- `nwb-intake`
- `dandi-explorer`
- `repro-enforcer`

### Milestone 3
- `spike-pipeline`
- `spike-train-analytics`

### Milestone 4
- `model-reproducer`
- `model-portability`

### Milestone 5
- human electrophysiology / BIDS expansion
- workflow bridges
- optional imaging lanes

## Quality gates

Do not mark work complete until all are true:

- [ ] tests exist
- [ ] at least one demo path exists
- [ ] benchmark entry exists or was updated
- [ ] catalog metadata is accurate
- [ ] docs reflect the implementation
- [ ] failure modes are documented
- [ ] reproducibility bundle is produced or explicitly stubbed with TODOs
- [ ] no hardcoded absolute paths
- [ ] no hidden network dependence in default tests

## Skill creation rules

When adding a skill:

1. Copy `templates/SKILL-TEMPLATE.md`
2. Fill in frontmatter completely
3. Keep one scientific job per skill
4. Add `examples/` and `tests/`
5. Add or update benchmark manifest entries
6. Regenerate `skills/catalog.json`
7. Add the skill to docs only after the metadata and tests are real

## Scientific safety rules

- Never invent thresholds, metadata fields, or archive semantics.
- Never silently coerce malformed neuroscience data into “valid” outputs.
- Always run or expose the relevant validator layer where one exists.
- Prefer failing clearly to producing misleading scientific artifacts.

## Pull request shape

Each PR should be small and reviewable:
- one milestone step or one skill at a time
- docs + tests + benchmark delta in the same PR
- explicit note if a networked benchmark is deferred

## Commands

```bash
python clawneuro.py list
python scripts/generate_catalog.py
python scripts/validate_benchmarks.py
python -m pytest -q
```

## Definition of done

A skill is done only when:
- a scientist can run it without the agent,
- a reviewer can inspect its methodology,
- a maintainer can benchmark it,
- and a coding agent can discover it from the catalog and SKILL.md alone.

