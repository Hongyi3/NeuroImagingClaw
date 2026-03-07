---
name: spike-pipeline
description: Run a standards-aware extracellular electrophysiology workflow with preprocessing, spike sorting, QC, and reporting.
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
  - raw-ephys
output_standard:
  - markdown-report
  - json-result
  - figures
  - tables
  - repro-bundle
validated_with:
  - NWB Inspector
  - pipeline-specific QC
backends:
  - SpikeInterface
benchmark_ids:
  - EPHYS-001
  - EPHYS-002
  - REPORT-001
trigger_keywords:
  - spike sorting
  - ephys qc
  - neuropixels
  - extracellular
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# spike-pipeline

## Purpose

Provide a benchmarkable, reproducible wrapper around the canonical extracellular ephys analysis path.

## Why this exists

Spike sorting workflows are powerful but operationally messy. A stable wrapper with explicit parameters, QC, and provenance is highly valuable to labs and reviewers.

## Inputs

Accept NWB or supported extracellular data via declared loaders. Require fixed preprocessing settings, explicit sorter choices, and output directories.

## Validators

Validate upstream data structure where applicable and run post hoc QC summaries on units, channels, and sorter outputs.

## Methodology

1. Load recording.
2. Apply declared preprocessing steps.
3. Run selected sorter or sorter profile.
4. Post-process and compute quality metrics.
5. Produce summary tables, figures, and provenance artifacts.

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

Unsupported source format, backend not installed, unstable sorter outputs, or invalid parameter combinations. All randomness and backend versions must be logged.

## Example queries

- Run the standard spike sorting pipeline on this recording.
- Generate a QC report for these extracellular data.
- Process this Neuropixels-style dataset reproducibly.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
