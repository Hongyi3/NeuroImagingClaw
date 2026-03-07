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

- valid BIDS dataset with anatomical input and optional BOLD runs
- participant selection plus optional output-space and reuse-derivative configuration
- optional local binary or pinned Docker/Apptainer image selection
- optional FreeSurfer license path when FreeSurfer-backed processing is enabled
- hard fail if anatomy is missing, if BOLD is missing for non-`anat_only` runs, or if a pinned runtime/license contract is violated

## Output contract

- `manifests/anat-bold-prep-summary.json`
- `report/anat-bold-prep-report.md`
- preserved upstream derivative root under `derivatives/`
- preserved subject HTML reports, confounds outputs, and citation boilerplate surfaced as manifest artifacts
- canonical `run-manifest.json` plus reproducibility bundle

## Failure modes

- non-BIDS inputs and anatomy-free datasets hard fail
- non-`anat_only` runs without BOLD hard fail
- unpinned container images and FreeSurfer-without-license requests hard fail at config validation
- executed runs become `partial` when preserved reports, boilerplate, or derivative metadata are missing after command success
- tracking suppression is enabled by default; disabling it is surfaced as a warning

## Non-goals

- statistical modeling
- connectivity post-processing
- hiding upstream warnings

## Chaining

Upstream: `bids_auditor`, `mriqc_report`
Downstream: `task_glm`, `rest_connectivity`, `report_bundle`

## Provenance

This skill must emit at least:

- exact preprocessing command lines;
- tool version or pinned container image reference;
- checksums of emitted wrapper artifacts;
- a machine-readable run manifest;
- pointers to preserved reports, boilerplate files, confounds outputs, and derivative metadata.
