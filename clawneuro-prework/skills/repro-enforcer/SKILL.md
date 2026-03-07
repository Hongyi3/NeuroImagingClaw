---
name: repro-enforcer
description: Create complete reproducibility bundles for any skill output, including commands, environment, checksums, and metadata.
version: 0.1.0
status: prototype
author: Core Team
license: MIT
trust_tier: core

tags:
  - neuroscience
  - reproducibility
  - multi

modality: multi
input_standard:
  - any
output_standard:
  - repro-bundle
validated_with:
  - bundle-integrity checks
backends:
benchmark_ids:
  - REPORT-001
  - REPRO-001
trigger_keywords:
  - reproducibility bundle
  - export environment
  - checksums
entrypoint: skills/repro-enforcer/repro_enforcer.py
demo_paths:
  - examples/synthetic/repro_seed_report.md
  - examples/synthetic/repro_seed_result.json
test_paths:
  - tests/test_catalog.py
  - tests/test_cli.py
  - tests/test_provenance.py
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# repro-enforcer

## Purpose

Make reproducibility a mandatory and uniform output across the entire repository.

## Why this exists

A platform like this is only as credible as its bundles. This skill centralizes bundle policy and reduces drift across modality-specific skills.

## Inputs

Accept outputs from any skill plus declared commands, environment notes, and artifact locations.

## Validators

Check that required files exist, that checksums can be computed, and that machine-readable output indexes all generated artifacts.

## CLI reference

```bash
# Standalone
python skills/repro-enforcer/repro_enforcer.py \
  --report examples/synthetic/repro_seed_report.md \
  --result examples/synthetic/repro_seed_result.json \
  --output outputs/repro-seed

# Reused by the foundation demo
python clawneuro.py demo foundation --output outputs/foundation-demo
```

## Methodology

1. Collect declared inputs and outputs.
2. Record commands and parameters.
3. Capture environment and hardware metadata.
4. Compute checksums.
5. Emit the bundle in a consistent layout.

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

Missing outputs, incomplete environment capture, or checksum generation errors. Incomplete bundles should fail loudly in tests.

## Example queries

- Create a reproducibility bundle for this analysis.
- Export this run with checksums and environment metadata.
- Package outputs for reviewer reruns.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
