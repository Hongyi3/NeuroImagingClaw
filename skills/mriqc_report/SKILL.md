---
name: mriqc_report
description: Run MRIQC and surface image quality metrics plus visual QC artifacts in a standardized reporting contract.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - mriqc-report
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - run mriqc
    - qc mri dataset
    - image quality metrics
---

# MRIQC Report

## Purpose

Run MRIQC and surface image quality metrics plus visual QC artifacts in a standardized reporting contract.

## Phase

Phase 2

## Upstream standards and tools

- MRIQC
- BIDS input contract
- NiPreps-style reporting

## Input contract

- valid BIDS dataset root with anatomical and/or BOLD content
- optional participant, session, and task filters
- optional modality filter limited to `anat` and `bold`
- optional local binary or pinned Docker/Apptainer image selection
- hard fail on invalid dataset state, missing requested participants/sessions, or unsupported modality mix

## Output contract

- `manifests/mriqc-summary.json`
- `report/mriqc-report.md`
- preserved upstream MRIQC derivative root under `derivatives/`
- preserved HTML reports and IQM tables surfaced as manifest artifacts
- canonical `run-manifest.json` plus reproducibility bundle

## Failure modes

- non-BIDS inputs or datasets without anatomical/BOLD data hard fail
- unpinned container images hard fail at config validation
- executed runs become `partial` when reports, IQM tables, or derivative metadata are missing after command success
- telemetry suppression is enabled by default; disabling it is surfaced as a warning

## Non-goals

- automatic exclusion of subjects without explicit policy
- pretending QC metrics imply biological validity

## Chaining

Upstream: `bids_auditor`
Downstream: `anat_bold_prep`, `report_bundle`

## Provenance

This skill must emit at least:

- exact participant and optional group command lines;
- tool version or pinned container image reference;
- checksums of emitted wrapper artifacts;
- a machine-readable run manifest;
- pointers to preserved upstream reports, IQM tables, and derivative metadata.
