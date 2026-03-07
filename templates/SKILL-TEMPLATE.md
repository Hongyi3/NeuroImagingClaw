---
name: your-skill-name
description: One-line description of the skill and the scientific problem it solves.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - mri
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - keyword phrase
    - another keyword phrase
---

# Skill name

## Purpose

What this skill does, why it exists, and what workflow state it expects.

## Upstream standards and tools

- BIDS / BIDS Derivatives / BIDS Stats Models as appropriate
- specific wrapped tools
- exact non-goals

## Input contract

- accepted input types;
- required metadata;
- validation behavior;
- what causes hard failure vs warning.

## Execution contract

1. validate input state
2. run wrapped tool(s)
3. collect outputs
4. write machine-readable manifest
5. write human-readable summary

## Output contract

Describe:

- derivative outputs;
- reports;
- tables;
- manifests;
- provenance artifacts.

## Provenance

Minimum files:

- commands
- versions
- checksums
- run manifest

## Failure modes

- unsupported input state
- missing metadata
- upstream tool failure
- partial-output behavior

## Benchmarks

Which track(s) this skill participates in and how success is measured.

## Chaining

Upstream and downstream skills.

## Example commands

```bash
# direct
python -m clawneuro.cli run your-skill-name --input /path/to/input --output /path/to/output

# orchestrated
python -m clawneuro.cli route --input /path/to/input --goal "describe the task"
```
