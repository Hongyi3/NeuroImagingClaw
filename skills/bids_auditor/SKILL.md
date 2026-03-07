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
- hard fail if the path is not a dataset root or cannot be read

## Output contract

- normalized validator JSON
- human-readable audit report
- categorized errors and warnings
- suggested remediation checklist

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
