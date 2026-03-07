# Codex Implementation Brief

This document translates the project strategy into an execution sequence for a coding agent.

## North star

Build the smallest version of ClawNeuro that already feels like durable field infrastructure.

## Absolute priorities

1. repository integrity
2. catalog + skill metadata tooling
3. reproducibility bundle scaffolding
4. NWB / DANDI lane
5. ephys pipeline lane
6. model reproduction lane
7. BIDS / OpenNeuro expansion

## Milestone 1 — foundation

Implement:
- catalog parsing and generation
- CLI listing and inspection
- benchmark manifest validation
- report / provenance directory helpers
- CI
- tests

Acceptance:
- `python clawneuro.py list` works
- catalog regenerates deterministically
- tests pass in CI
- benchmark manifest validates

## Milestone 2 — NWB / DANDI lane

Implement:
- `nwb-intake`
- `dandi-explorer`
- `repro-enforcer`

Acceptance:
- public tiny or synthetic NWB example loads
- validation hooks are exposed
- manifest + report + bundle are produced

## Milestone 3 — extracellular ephys lane

Implement:
- `spike-pipeline`
- `spike-train-analytics`

Acceptance:
- synthetic smoke benchmark runs deterministically
- at least one public benchmark task is defined
- QC outputs are reproducible

## Milestone 4 — models lane

Implement:
- `model-reproducer`
- `model-portability`

Acceptance:
- at least one public model reproduces a canonical trace or figure
- backend assumptions are explicit
- provenance captures simulator and environment details

## Milestone 5 — expansion

Implement:
- `human-ephys-bids`
- optional MNE-BIDS and validator support
- thin workflow bridges
- additional reporting polish

Acceptance:
- one public BIDS example validates and round-trips through the relevant interface
- no regression in core NWB and model lanes

## Coding rules

- keep orchestration code thin
- isolate backend adapters
- keep every skill runnable without the orchestrator
- never hardcode public dataset assumptions without pinning them in benchmark metadata
- do not silently skip validation
- prefer explicit failure messages over “best effort” data coercion

## Documentation rules

When a milestone lands, update:
- README if user-facing behavior changed
- skill `SKILL.md`
- `skills/catalog.json`
- benchmark manifest
- changelog

## Final principle

If forced to choose between:
- broader feature coverage, and
- a smaller but benchmarked, reproducible, publication-ready core,

always choose the smaller, benchmarked core.

