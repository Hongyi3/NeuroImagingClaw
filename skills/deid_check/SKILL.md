---
name: deid_check
description: Assess whether a BIDS dataset is technically ready for open sharing, with emphasis on structural-image privacy handling.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - de-identification-check
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - deface check
    - openneuro ready
    - deidentify mri
---

# De-identification Check

## Purpose

Assess whether a BIDS dataset is technically ready for open sharing, with emphasis on structural-image privacy handling.

## Phase

Phase 1

## Upstream standards and tools

- OpenNeuro upload rules
- defacing and export-readiness checks
- local metadata inspection

## Input contract

- BIDS root directory
- optional policy profile such as OpenNeuro-ready
- hard fail if anatomical assets are unreadable

## Output contract

- export-readiness checklist
- structural-image privacy status
- warnings about unresolved sharing blockers
- machine-readable shareability summary
- rule results that cite the governing privacy and methods policies

## Non-goals

- legal or ethics certification
- publishing or uploading data automatically

## Chaining

Upstream: `bids_auditor`
Downstream: `report_bundle` and optional upload workflows added in the future

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.

## Failure modes

- unreadable or non-BIDS dataset root;
- missing anatomical sidecars for detected structural images;
- structural images without explicit defacing or face-removal metadata.

## Fidelity limitations

- this skill reports technical sharing readiness only;
- it does not certify consent, ethics approvals, or data-use permissions;
- conservative rule failures are preferred over permissive guesses.
