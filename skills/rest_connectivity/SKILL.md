---
name: rest_connectivity
description: Run connectivity-oriented postprocessing from preprocessed derivatives for resting-state or pseudo-resting-state analyses.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - resting-state-connectivity
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - rest connectivity
    - xcp-d
    - functional connectivity
---

# Resting-State Connectivity

## Purpose

Run connectivity-oriented postprocessing from preprocessed derivatives for resting-state or pseudo-resting-state analyses.

## Phase

Phase 3

## Upstream standards and tools

- XCP-D
- connectivity-oriented time series and matrix outputs
- fMRIPrep-compatible derivatives

## Input contract

- preprocessed derivatives appropriate for resting-state or pseudo-resting-state analysis
- connectivity configuration and atlas choices
- hard fail if the requested job is actually a general task GLM workflow

## Output contract

- denoised outputs as appropriate
- timeseries and connectivity matrices
- additional QC measures
- manifest of atlas and postprocessing choices

## Non-goals

- general task GLM
- claiming suitability for every task-based downstream analysis

## Chaining

Upstream: `anat_bold_prep`
Downstream: `report_bundle`

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
