---
name: model-portability
description: Assess and improve cross-simulator portability using portable model representations where appropriate.
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
  - NeuroML
  - PyNN
  - simulator-model
output_standard:
  - markdown-report
  - json-result
  - figures
  - tables
  - repro-bundle
validated_with:
  - portability checks
backends:
  - NeuroML
  - PyNN
  - NEURON
  - NEST
  - Brian2
benchmark_ids:
  - MODEL-PORT-001
  - REPORT-001
trigger_keywords:
  - neuroml
  - pynn
  - portability
  - cross simulator
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# model-portability

## Purpose

Turn model portability into an explicit, testable feature instead of a vague aspiration.

## Why this exists

Cross-simulator portability is one of the clearest ways to make model reuse durable. It is also a strong scientific differentiator for ClawNeuro.

## Inputs

Accept portable model specifications or models that can be translated into portable forms. Require explicit portability targets.

## Validators

Validate syntax and declared portability targets. Capture unsupported components and translation loss clearly.

## Methodology

1. Inspect the model representation.
2. Attempt translation or execution across declared backends.
3. Compare agreed-upon output targets.
4. Summarize parity, divergence, and blockers.

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

Unsupported simulator features, translation gaps, or output divergence beyond declared tolerance. Never describe portability as successful when major assumptions changed silently.

## Example queries

- Test whether this model can run across NEURON and NEST.
- Evaluate the portability of this NeuroML model.
- Compare output parity across simulators.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
