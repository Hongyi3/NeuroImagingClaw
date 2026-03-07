# Benchmark Specification

## Purpose

The benchmark suite is part of the product, not an afterthought. ClawNeuro should earn trust through
public, repeatable evidence on public BIDS datasets.

## Benchmark tracks

### 1. Smoke / CI track

Purpose:

- verify BIDS handling and skill wiring quickly;
- catch regressions in catalogs, manifests, and report generation.

Sources:

- `bids-examples`
- tiny synthetic or empty-file fixtures where appropriate

### 2. Task-fMRI track

Purpose:

- validate anatomical + BOLD preprocessing;
- validate events / confounds handling;
- validate task GLM workflow assembly and reporting.

Candidate public datasets:

- `ds003452` (`DMCC13benchmark`)
- `ds003020`
- additional small-to-medium OpenNeuro task datasets after acceptance review

### 3. Resting-state track

Purpose:

- validate preprocessing -> connectivity post-processing;
- validate QC metrics, time series, and connectivity outputs.

Candidate public datasets:

- `ds003673`
- `ds001168`
- additional OpenNeuro resting-state datasets after acceptance review

### 4. Diffusion track

Purpose:

- validate diffusion preprocessing and later reconstruction.

Candidate public datasets:

- `ds002087`
- `ds005664`
- additional public diffusion datasets after acceptance review

### 5. Growth / multimodal track

Purpose:

- stress-test orchestration, metadata, and reporting across richer studies.

Candidate public datasets:

- `ds006731`
- `ds007345`

## Metrics

- conversion success rate;
- validation errors / warnings by category;
- preprocessing completion rate;
- report completeness;
- runtime and peak resource profile;
- reproducibility of reruns;
- agreement with upstream baseline outputs when appropriate;
- percentage of runs that emit publication-ready methods and provenance bundles.

## Acceptance criteria for a benchmark dataset

A benchmark candidate should be:

- public;
- legally straightforward to use;
- BIDS-valid or close enough that validator behavior is itself informative;
- representative of a real target use case;
- small enough for at least one practical automated benchmark path.

## Benchmark rules

- Do not cherry-pick only easy internal datasets.
- Freeze benchmark versions for public comparisons.
- Record container tags, exact commands, and hashes.
- Keep smoke tests separate from substantive scientific benchmarks.
- Treat benchmark failures as release blockers when they affect core contracts.

## Baseline comparison philosophy

ClawNeuro is not trying to “beat” upstream tools numerically in preprocessing. Its claims should focus on:

- orchestration reliability;
- provenance completeness;
- packaging quality;
- publication readiness;
- reproducibility;
- auditability.
