---
name: report_bundle
description: Assemble a publication-ready dossier that combines QC, preprocessing, modeling, and provenance into one coherent output.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - report-bundle
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - make report bundle
    - manuscript methods
    - analysis dossier
---

# Report Bundle

## Purpose

Assemble a publication-ready dossier that combines QC, preprocessing, modeling, and provenance into one coherent output.

## Phase

Phase 3

## Upstream standards and tools

- upstream skill reports
- deterministic report templates
- methods and provenance policies

## Input contract

- one or more completed ClawNeuro skill outputs
- optional study metadata for branding / manuscript context
- hard fail if core manifests are missing

## Output contract

- executive summary
- methods text
- figures and tables index
- warnings and QC summary
- bibliography hints
- HTML/Markdown/PDF-ready source bundle

## Non-goals

- fabricating missing methods details
- hiding failed or partial upstream steps

## Chaining

Upstream: all major analysis skills
Downstream: manuscript preparation and archival release

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
