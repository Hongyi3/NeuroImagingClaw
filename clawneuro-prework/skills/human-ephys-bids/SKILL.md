---
name: human-ephys-bids
description: Read, validate, and prepare BIDS-compliant human electrophysiology datasets for analysis and publication.
version: 0.1.0
status: planned-phase-2
author: Core Team
license: MIT
trust_tier: core

tags:
  - neuroscience
  - reproducibility
  - human-ephys

modality: human-ephys
input_standard:
  - BIDS
  - OpenNeuro
output_standard:
  - markdown-report
  - json-result
  - bids-validation-report
  - repro-bundle
validated_with:
  - BIDS Validator
backends:
  - MNE
  - MNE-BIDS
benchmark_ids:
  - BIDS-001
  - REPORT-001
trigger_keywords:
  - bids eeg
  - openneuro
  - mne-bids
  - ieeg bids
  - meg bids
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# human-ephys-bids

## Purpose

Provide a phase-2 pathway for human EEG, MEG, iEEG, and related BIDS-compliant workflows.

## Why this exists

BIDS and OpenNeuro are central to human neuroimaging and electrophysiology. This skill belongs in ClawNeuro, but after the NWB/ephys/model core is stable.

## Inputs

Accept BIDS dataset directories and OpenNeuro-sourced public datasets. Require validator-ready directory structure.

## Validators

Run the BIDS Validator and capture warnings and errors explicitly. Encourage round-trip compatibility checks with MNE-BIDS.

## Methodology

1. Validate the dataset structure.
2. Load via the appropriate BIDS-aware interface.
3. Summarize modality, participants, sessions, and tasks.
4. Emit validation and provenance artifacts.

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

Invalid BIDS layout, missing metadata sidecars, unsupported modality details, or round-trip write failures.

## Example queries

- Validate this EEG-BIDS dataset.
- Summarize this OpenNeuro dataset.
- Prepare this iEEG-BIDS dataset for analysis.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
