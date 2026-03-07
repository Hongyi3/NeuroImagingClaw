---
name: dandi-explorer
description: Discover, cache, summarize, and prepare public DANDI assets for downstream neurophysiology workflows.
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
  - DANDI
  - NWB
  - BIDS
output_standard:
  - markdown-report
  - json-result
  - dataset-card
  - repro-bundle
validated_with:
  - DANDI metadata checks
backends:
  - DANDI API / CLI
benchmark_ids:
  - DANDI-001
  - REPORT-001
trigger_keywords:
  - dandi
  - dandiset
  - public neurophysiology dataset
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# dandi-explorer

## Purpose

Make public DANDI data discoverable and usable without forcing users to manually navigate archive mechanics first.

## Why this exists

Public archive reuse is high leverage but still awkward. This skill should bridge archive metadata, asset access, and downstream analysis readiness.

## Inputs

Accept Dandiset identifiers, asset URLs, or search parameters for public DANDI content. Private data handling should remain opt-in and explicit.

## Validators

Validate archive metadata availability and asset-access assumptions. Record remote-access mode and cache policy in provenance.

## Methodology

1. Resolve archive identifiers or search queries.
2. Collect dataset metadata and candidate assets.
3. Optionally cache or stream public assets.
4. Emit a dataset card and machine-readable manifest.
5. Hand off to downstream skills when requested.

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

Invalid identifiers, unavailable assets, remote access problems, or archive metadata drift. Provenance should note whether content was streamed, cached, or fully downloaded.

## Example queries

- Summarize Dandiset 000027 and prepare it for analysis.
- Find a public DANDI dataset with extracellular electrophysiology.
- Generate a dataset card for this DANDI asset.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
