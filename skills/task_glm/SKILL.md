---
name: task_glm
description: Estimate first-level task-fMRI models from preprocessed derivatives using explicit model specifications rather than ad hoc prompts.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - task-glm
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - task glm
    - first level fmri
    - fit bids stats model
---

# Task GLM

## Purpose

Estimate first-level task-fMRI models from preprocessed derivatives using explicit model specifications rather than ad hoc prompts.

## Phase

Phase 3

## Upstream standards and tools

- BIDS Stats Models
- FitLins and/or Nilearn
- fMRIPrep-compatible derivatives

## Input contract

- preprocessed derivatives
- events/confounds data
- model JSON or generated draft model
- hard fail if task design inputs are missing or ambiguous

## Output contract

- model outputs and summaries
- design and contrast records
- methods-ready modeling description
- manifest linking statistics to inputs and model spec

## Non-goals

- resting-state connectivity
- silently choosing task regressors without surfacing the model spec

## Chaining

Upstream: `anat_bold_prep`
Downstream: `report_bundle`, future group-level modeling skills

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
