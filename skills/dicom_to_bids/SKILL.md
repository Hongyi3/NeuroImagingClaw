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
- explicit participant label for the target BIDS subject
- optional session label
- optional Dcm2Bids JSON config or HeuDiConv heuristic
- optional participant/session mapping metadata
- hard fail if the input is not readable as a supported imaging source

## Output contract

- BIDS directory tree
- conversion manifest with structured conversion, runtime evidence, and post-validation step records
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
- resolved runtime paths or pinned image references;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.

## Failure modes

- unreadable non-DICOM input;
- missing Dcm2Bids config or HeuDiConv heuristic for execution-ready conversion;
- missing `dcm2niix` dependency even when `dcm2bids` itself is installed;
- executed conversion with incomplete runtime proof, which must be reported as `partial` rather than
  `succeeded`;
- unpinned container image when Docker or Apptainer execution is requested;
- post-conversion validation skipped because curation failed upstream.

## Wrapper behavior

- when upstream curation omits `dataset_description.json`, the wrapper writes a minimum BIDS root
  description and flags it for review;
- upstream `tmp_dcm2bids` output is treated as internal execution state and removed before
  post-conversion validation;
- a run is only marked `succeeded` when execution, logs, manifests, and runtime proof are all
  present.

## Fidelity limitations

- M3 validates the Dcm2Bids 3.x command surface and the public `dcm_qa_nih` tutorial path;
- HeuDiConv remains supported as a planning target but is not evidence-backed for M3;
- successful public-case conversion evidence now exists under
  `benchmarks/artifacts/phase1_dcm_qa_nih/`;
- Docker and Apptainer request planning are covered, but local container execution is still not
  verified in this inspected workspace.
