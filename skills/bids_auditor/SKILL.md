---
name: bids_auditor
description: Validate and summarize the structural integrity and metadata completeness of a BIDS dataset.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - bids-auditor
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - validate bids
    - audit dataset
    - bids validator
---

# BIDS Auditor

## Purpose

Validate and summarize the structural integrity and metadata completeness of a BIDS dataset.

## Phase

Phase 1

## Upstream standards and tools

- BIDS
- BIDS Validator
- optional BIDS schema-driven checks

## Input contract

- BIDS root directory
- optional ignore rules or policy profile
- optional validator config JSON when upstream ignore rules or schema settings must be explicit
- hard fail if the path is not a dataset root or cannot be read

## Output contract

- normalized validator JSON
- human-readable audit report
- categorized errors and warnings
- suggested remediation checklist
- machine-readable evidence metadata indicating whether the summary came from a planned command, a
  live run, or a pinned fidelity fixture

## Non-goals

- modifying datasets automatically without explicit user action
- claiming scientific quality from validator success alone

## Chaining

Upstream: `dicom_to_bids` or user-provided BIDS dataset
Downstream: all execution skills

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.

## Failure modes

- unreadable or non-BIDS input root;
- missing validator executable or container runtime during `execute=True`;
- unpinned container image when Docker or Apptainer execution is requested;
- validator stdout that cannot be parsed as JSON.

## Fidelity limitations

- M3 fidelity coverage is anchored to a pinned excerpt from a public `bids-examples/ds005`
  validator run, not to a checked-in full validator output tree;
- the wrapper normalizes both legacy `issues.errors`/`issues.warnings` JSON and current
  `issues.issues` JSON, but additional upstream formats must be added explicitly if they appear.
