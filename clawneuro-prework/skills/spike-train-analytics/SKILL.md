---
name: spike-train-analytics
description: Compute canonical spike-train and related electrophysiology summaries with a reproducible reporting layer.
version: 0.1.0
status: planned
author: Core Team
license: MIT
trust_tier: core

tags:
  - neuroscience
  - reproducibility
  - ephys

modality: ephys
input_standard:
  - NWB
  - sorted-units
output_standard:
  - markdown-report
  - json-result
  - figures
  - tables
  - repro-bundle
validated_with:
  - input-structure checks
backends:
  - Elephant
benchmark_ids:
  - SPIKE-001
  - REPORT-001
trigger_keywords:
  - psth
  - correlogram
  - firing rate
  - synchrony
  - spike train analysis
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# spike-train-analytics

## Purpose

Run a small, disciplined set of downstream analyses on sorted units and related time-series data.

## Why this exists

Downstream analyses are often reimplemented inconsistently. A narrow, conservative skill reduces methodological drift and improves report quality.

## Inputs

Accept sorted spike trains or compatible NWB-derived structures. Require explicit time-window and parameter declarations where applicable.

## Validators

Check time bases, unit consistency, and required metadata before analysis. Emit warnings for underspecified analyses.

## Methodology

1. Normalize input representations.
2. Compute declared summaries such as rates, correlograms, and synchrony measures.
3. Generate standard visualizations and tables.
4. Capture parameters and time windows in provenance.

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

Mismatched time units, missing spike metadata, inappropriate parameterization, or ill-posed small-sample analyses.

## Example queries

- Compute PSTHs and correlograms for these sorted units.
- Summarize firing rates and synchrony.
- Run a standard spike-train analysis report.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
