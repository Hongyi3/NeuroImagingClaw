---
name: dicom_to_bids
description: Convert DICOM directories or scanner exports into an auditable BIDS dataset using wrapped conversion and curation tools.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - dicom-to-bids
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - dicom to bids
    - bidsify mri data
    - convert scanner export
---

# DICOM to BIDS

## Purpose

Convert DICOM directories or scanner exports into an auditable BIDS dataset using wrapped conversion and curation tools.

## Phase

Phase 1

## Upstream standards and tools

- BIDS
- dcm2niix
- HeuDiConv and/or Dcm2Bids
- BIDS Validator for post-conversion checks

## Input contract

- DICOM directory, NIfTI staging directory, or scanner export folder
- optional heuristic file or mapping config
- optional participant/session mapping metadata
- hard fail if the input is not readable as a supported imaging source

## Output contract

- BIDS directory tree
- conversion manifest
- copied or linked sidecars as appropriate
- validator summary after conversion
- a curation checklist for unresolved metadata gaps

## Non-goals

- downstream QC or preprocessing
- inferring study design from thin metadata without surfacing uncertainty

## Chaining

Upstream: raw scanner output
Downstream: `bids_auditor`, `deid_check`, `mriqc_report`, `anat_bold_prep`

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
