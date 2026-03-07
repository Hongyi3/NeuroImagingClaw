---
name: your-skill-name
description: One-line description of what this neuroscience skill does.
version: 0.1.0
status: planned
author: Your Name
license: MIT
trust_tier: experimental

tags:
  - neuroscience
  - reproducibility

modality: one-of[ephys, imaging, models, human-ephys, multi]
input_standard:
  - NWB
output_standard:
  - markdown-report
  - json-result
validated_with:
  - relevant-validator
backends:
  - relevant-backend
benchmark_ids:
  - BENCH-001
trigger_keywords:
  - phrase that should route here
  - another phrase
entrypoint: skills/your-skill-name/your_skill.py
demo_paths:
  - examples/synthetic/your-skill-demo-input.json
test_paths:
  - tests/test_your_skill.py

requires:
  python:
    - python>=3.11
  packages:
    - package-name
  bins: []
---

# Skill Name

You are **Skill Name**, a specialized ClawNeuro skill for [domain].

## Purpose

State the scientific job of the skill in one sentence.

## Why this exists

- Without it: describe the common failure mode or friction
- With it: describe the automated outcome
- Why ClawNeuro: explain why this belongs in a standards-native skill library rather than generic chat

## Inputs

Describe:
- accepted file types
- accepted standards
- minimal metadata assumptions
- when the skill should refuse to run

## Validators

List:
- schema validator(s)
- best-practice validator(s)
- numerical or structural checks

## CLI reference

```bash
# Standalone
python skills/your-skill-name/your_skill.py --input <path> --output <dir>

# Demo / smoke mode
python skills/your-skill-name/your_skill.py --demo --output <dir>

# Via orchestrator (future)
python clawneuro.py show your-skill-name
```

## Methodology

1. Load input or fetch public asset.
2. Validate structure and metadata.
3. Execute the declared backend workflow.
4. Collect outputs into standardized tables and figures.
5. Emit reproducibility artifacts.

### Key parameters / choices
- Parameter: value or policy
- Numerical tolerance: declare if needed
- Randomness policy: fixed seed or deterministic requirement

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

Document:
- malformed metadata
- unsupported format variants
- validator failures
- backend incompatibilities
- numerical instability risks

## Example queries

- “Example query 1”
- “Example query 2”
- “Example query 3”

## Acceptance tests

- define a demo path
- define at least one benchmark mapping
- define what counts as success
- if status is not `planned` or `planned-phase-2`, frontmatter must include a real `entrypoint`, `demo_paths`, and `test_paths`

## Safety and provenance

- local-first by default
- explicit network use only for public archives
- no silent metadata fabrication
- log commands, environment, and checksums
