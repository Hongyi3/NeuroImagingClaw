---
name: diffusion_prep
description: Wrap diffusion-MRI preprocessing and later reconstruction handoff within the same provenance and reporting framework.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - diffusion-preprocessing
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - diffusion prep
    - qsiprep
    - dwi preprocessing
---

# Diffusion Preprocessing

## Purpose

Wrap diffusion-MRI preprocessing and later reconstruction handoff within the same provenance and reporting framework.

## Phase

Phase 4

## Upstream standards and tools

- QSIPrep
- QSIRecon handoff path
- BIDS diffusion inputs

## Input contract

- valid BIDS dataset with DWI and required metadata
- diffusion configuration
- hard fail when required DWI acquisition metadata is insufficient for the requested workflow

## Output contract

- diffusion derivatives
- visual reports and QC metrics
- reconstruction handoff metadata
- run manifest

## Non-goals

- launching with every advanced reconstruction path enabled by default

## Chaining

Upstream: `bids_auditor`, `deid_check`
Downstream: `report_bundle`, future diffusion reconstruction skills

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
