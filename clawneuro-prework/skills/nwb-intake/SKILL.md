---
name: nwb-intake
description: Load, validate, inspect, and summarize NWB files into machine-readable manifests and human-readable reports.
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
output_standard:
  - markdown-report
  - json-result
  - nwb-manifest
  - repro-bundle
validated_with:
  - PyNWB validator
  - NWB Inspector
backends:
  - PyNWB
  - NWB Inspector
benchmark_ids:
  - NWB-001
  - REPORT-001
trigger_keywords:
  - nwb file
  - inspect nwb
  - validate nwb
  - summarize nwb
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# nwb-intake

## Purpose

Turn an NWB file into a validated, explicit summary that downstream skills and humans can trust.

## Why this exists

NWB is powerful but opaque to many users. A strong intake skill makes archive reuse, debugging, and downstream routing much easier.

## Inputs

Accept `.nwb` files or directories of NWB assets. Require readable files and enough metadata to identify subject, session, and acquisition context where present.

## Validators

Run strict schema validation and best-practice inspection. Surface issues in the report and machine-readable output instead of hiding them.

## Methodology

1. Load NWB via the reference API.
2. Validate schema compliance.
3. Run best-practice inspection.
4. Extract standardized manifest fields.
5. Emit report + manifest + reproducibility bundle.

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

Unreadable files, invalid schema, unsupported extensions, or metadata inconsistencies. The skill should surface failures clearly and preserve validator output.

## Example queries

- Inspect this NWB file.
- Validate this neurophysiology dataset and tell me what it contains.
- Create a dataset card for this NWB session.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
