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

- valid BIDS dataset
- optional participant filters
- hard fail on invalid dataset state or unsupported modality mix for the requested run

## Output contract

- MRIQC derivatives
- preserved visual reports
- standardized summary tables
- QC flags and run manifest

## Non-goals

- automatic exclusion of subjects without explicit policy
- pretending QC metrics imply biological validity

## Chaining

Upstream: `bids_auditor`
Downstream: `anat_bold_prep`, `report_bundle`

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
