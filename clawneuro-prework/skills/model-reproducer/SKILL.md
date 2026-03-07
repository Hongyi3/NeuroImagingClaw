---
name: model-reproducer
description: Fetch, configure, run, and document public computational neuroscience models to recreate canonical outputs.
version: 0.1.0
status: planned
author: Core Team
license: MIT
trust_tier: core

tags:
  - neuroscience
  - reproducibility
  - models

modality: models
input_standard:
  - ModelDB
  - Open Source Brain
  - simulator-model
output_standard:
  - markdown-report
  - json-result
  - figures
  - tables
  - repro-bundle
validated_with:
  - model-run checks
backends:
  - NEURON
  - Brian2
  - NEST
benchmark_ids:
  - MODEL-001
  - MODEL-002
  - REPORT-001
trigger_keywords:
  - reproduce model
  - modeldb
  - open source brain
  - neuron model
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# model-reproducer

## Purpose

Make public published computational models runnable, auditable, and comparable through a common execution layer.

## Why this exists

Model reuse is central to computational neuroscience, yet published code often remains fragile. A strong reproduction skill makes model reuse far more practical.

## Inputs

Accept public model repository identifiers, local model directories, or simulator-specific project files. Require explicit target outputs or canonical reference traces where possible.

## Validators

Check model availability, backend compatibility, and declared output targets. Capture simulator version and platform notes.

## Methodology

1. Resolve the public model or local source.
2. Prepare the execution environment.
3. Run the model with declared backend settings.
4. Extract canonical traces or figures.
5. Emit a comparison-focused report and bundle.

## Outputs

```text
output/
├── report.md
├── result.json
├── figures/
├── tables/
└── reproducibility/
    ├── commands.sh
    ├── environment.yml
    ├── hardware.json
    ├── random_seeds.json
    └── checksums.sha256
```

## Failure modes

Broken upstream code, simulator incompatibility, undocumented dependencies, or missing canonical figure targets. The report should distinguish platform failures from scientific mismatches.

## Example queries

- Reproduce this published neuron model.
- Run a ModelDB model and regenerate the reference trace.
- Package this public model into a reproducible report.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
