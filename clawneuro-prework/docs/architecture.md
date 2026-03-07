# Architecture

## Design goal

ClawNeuro should make the field’s standards and canonical workflows:
- easy to discover,
- safe to execute,
- straightforward to benchmark,
- trivial to reproduce later.

## System overview

```text
User request / file input
        |
        v
+-----------------------+
|  Neuro Orchestrator   |
| routing + planning    |
| report assembly       |
+----------+------------+
           |
  +--------+--------+-----------------------------+
  |                 |                             |
  v                 v                             v
NWB/DANDI       BIDS/OpenNeuro             Models / Simulation
skills          skills                     skills
  |                 |                             |
  +--------+--------+-----------------------------+
           |
           v
+-----------------------+
| Repro Enforcer        |
| bundle + manifest     |
| checksums + env       |
+----------+------------+
           |
           v
 report.md / result.json / figures / tables / containers / commands
```

## Architectural principles

### 1. Standards before project-local conventions
The orchestrator should route to standards-aware skills, not invent a new global intermediate format unless one is clearly justified.

### 2. Skills remain single-responsibility
The orchestrator chains them. Skills stay narrow.

### 3. Validators are first-class
Where the ecosystem has a validator, the corresponding skill should expose it:
- PyNWB validator
- NWB Inspector
- BIDS Validator
- simulator or model-validation checks where applicable

### 4. Reports are compositional
The final report can be a stitched product of multiple skill outputs, but the component outputs must remain independently inspectable.

### 5. Reproducibility is universal
Every skill emits enough information to rerun the work outside the agent.

## Execution profiles

## local
Default path. Suitable for:
- demos
- CI fixtures
- workstation workflows
- notebook-sized public datasets

## cached-object-store
For public large datasets where “download everything first” is wasteful.

Characteristics:
- local metadata and manifests
- asset references or streaming handles
- optional local cache
- explicit byte-range / remote access notes in provenance

## hpc
For shared clusters or institutional compute.

Requirements:
- scheduler-friendly execution
- container-first
- Apptainer compatibility
- deterministic command logging
- hardware notes captured in the bundle

## Repository modules

## orchestrator
Task routing, planning, multi-skill chaining.

Milestone 1 implementation status:
- repository CLI and `skills/neuro-orchestrator/orchestrator.py` provide deterministic routing by explicit skill name, file suffix, standards hints, modality hints, and trigger keywords;
- ambiguous or empty routes fail explicitly with machine-readable JSON output.

## registry
Skill discovery, catalog loading, metadata validation.

## standards
Adapters and utilities for NWB, BIDS, NeuroML, PyNN, and archive metadata.

## provenance
Bundle generation, checksums, environment and hardware capture.

Milestone 1 implementation status:
- `skills/repro-enforcer/repro_enforcer.py` and `src/clawneuro/provenance.py` emit the standard bundle layout;
- `result.json` indexes generated artifacts and `reproducibility/checksums.sha256` covers every indexed file;
- a deterministic foundation demo exercises the routing and provenance layers without network access.

## report
Markdown-first output assembly, with machine-readable companion files.

## benchmarks
Benchmark definitions, expected outputs, scoring logic, smoke and release panels.

## Trust model

Every skill declares a `trust_tier`:
- `core`
- `reviewed-community`
- `experimental`

Routing policy:
- `core` is eligible for default routing
- `reviewed-community` is opt-in or confidence-weighted
- `experimental` is never selected silently

## Remote compute policy

ClawNeuro should not become a cloud platform, but it should understand public data access patterns well enough to support:
- remote public archive access,
- local caching,
- institutional HPC submission,
- reproducible environment capture for both.

That keeps the project local-first while still supporting “data-adjacent” execution for large public datasets.
