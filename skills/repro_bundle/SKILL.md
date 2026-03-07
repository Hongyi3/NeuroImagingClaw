---
name: repro_bundle
description: Package exact commands, environments, hashes, manifests, and optional DataLad provenance into a rerunnable bundle.
version: 0.1.0
author: ClawNeuro maintainers
license: MIT
tags:
  - neuroimaging
  - bids
  - reproducibility-bundle
metadata:
  requires: always
  homepage: https://github.com/YOUR-ORG/ClawNeuro
  os:
    - linux
    - macos
  trigger_keywords:
    - repro bundle
    - make reproducible
    - rerun package
---

# Reproducibility Bundle

## Purpose

Package exact commands, environments, hashes, manifests, and optional DataLad provenance into a rerunnable bundle.

## Phase

Phase 3

## Upstream standards and tools

- shared run manifests
- environment capture
- optional DataLad integration

## Input contract

- completed run directory
- optional release or archival configuration
- hard fail if core execution metadata is missing

## Output contract

- commands
- environment lock
- checksums
- analysis log
- replay manifest
- optional DataLad provenance notes

## Non-goals

- pretending a run is reproducible when critical metadata is absent

## Chaining

Upstream: all skills
Downstream: release engineering, benchmarks, publication artifacts

## Provenance

This skill must emit at least:

- exact command lines;
- tool versions;
- checksums of primary inputs;
- a machine-readable run manifest;
- pointers to any derivative dataset descriptions it creates or updates.
