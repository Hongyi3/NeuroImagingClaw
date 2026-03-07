---
name: anat_bold_prep
description: Wrap fMRIPrep-like anatomical and BOLD preprocessing into a stable skill with harvested reports and derivative metadata.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - anatomical-and-bold-preprocessing
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - run fmriprep
    - preprocess bold
    - anat bold prep
---

# Anatomical and BOLD Preprocessing

## Purpose

Wrap fMRIPrep-like anatomical and BOLD preprocessing into a stable skill with harvested reports and derivative metadata.

## Phase

Phase 2

## Upstream standards and tools

- fMRIPrep
- BIDS Derivatives
- TemplateFlow
- optional FreeSurfer-enabled pathways

## Input contract

- valid BIDS dataset with T1w and optional BOLD runs
- preprocessing configuration
- participant selection
- hard fail if required metadata or mandatory modalities are missing

## Output contract

- preprocessed BIDS derivatives
- upstream visual reports
- collected boilerplate and versions
- normalized ClawNeuro run manifest

## Non-goals

- statistical modeling
- connectivity post-processing
- hiding upstream warnings

## Chaining

Upstream: `bids_auditor`, `mriqc_report`
Downstream: `task_glm`, `rest_connectivity`, `report_bundle`

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
