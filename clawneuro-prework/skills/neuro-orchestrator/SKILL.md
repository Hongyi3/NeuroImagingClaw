---
name: neuro-orchestrator
description: Route requests to neuroscience skills by modality, format, and intent, then assemble a unified report.
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
  - NWB
  - BIDS
  - NeuroML
  - PyNN
output_standard:
  - markdown-report
  - json-result
  - repro-bundle
validated_with:
backends:
benchmark_ids:
  - ARCH-001
  - REPORT-001
trigger_keywords:
  - route workflow
  - orchestrate skills
  - plan neuroscience workflow
entrypoint: skills/neuro-orchestrator/orchestrator.py
demo_paths:
  - examples/synthetic/foundation_request.json
  - examples/synthetic/session_stub.nwb
test_paths:
  - tests/test_catalog.py
  - tests/test_cli.py
  - tests/test_routing.py
requires:
  python:
    - python>=3.11
  packages: []
  bins: []
---

# neuro-orchestrator

## Purpose

Route files and requests to the correct neuroscience skill and compose the final output bundle.

## Why this exists

Without an orchestrator, users must know the exact tool and file conventions in advance. With it, the repository behaves like a coherent platform instead of a bag of scripts.

## Inputs

Accept file paths, directories, and explicit task requests. Inspect file extensions, archive metadata, and catalog trigger keywords. Refuse ambiguous destructive actions or unsupported private-cloud workflows.

## Validators

Validate routing metadata against the skill catalog. Ensure only eligible trust tiers are selected by default.

## CLI reference

```bash
# Standalone
python skills/neuro-orchestrator/orchestrator.py --query "Inspect this NWB file" --input examples/synthetic/session_stub.nwb

# Via repository CLI
python clawneuro.py route --query "Inspect this NWB file" --input examples/synthetic/session_stub.nwb --json

# Deterministic foundation demo
python clawneuro.py demo foundation --output outputs/foundation-demo
```

## Methodology

1. Inspect input files and task text.
2. Score candidate skills by modality, standard, and keyword alignment.
3. Build an execution plan.
4. Run eligible skills in order.
5. Merge their outputs into a single final report.

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

Ambiguous modality, missing files, or conflicting standards metadata. Route failure should be explicit and should not invent missing scientific context.

## Example queries

- Summarize this NWB file and tell me which downstream skills apply.
- Run the standard ephys pipeline on this public DANDI asset.
- Reproduce this published neuron model and give me a report.

## Acceptance tests

- A deterministic demo or smoke path exists.
- Every benchmark ID in frontmatter is represented in `benchmarks/manifest.json`.
- The bundle is emitted with complete provenance metadata.
