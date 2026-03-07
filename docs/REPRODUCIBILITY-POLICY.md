# Reproducibility Policy

## Core rule

No run is complete without a reproducibility bundle.

## Minimum required bundle

- `commands.sh`
- `environment.yml` or equivalent lockfile
- `checksums.sha256`
- `analysis_log.md`
- `run-manifest.json`

## Preferred extended bundle

- container tags and digests;
- input inventory;
- output inventory;
- benchmark metadata;
- DataLad provenance when enabled;
- exact derivative metadata snapshots.

## Reproducibility levels

### Level 1 — basic

Can rerun the same commands with the same inputs and environment definition.

### Level 2 — strong

Can rerun with pinned containers and compare outputs programmatically.

### Level 3 — archival

Data, code, containers, and provenance are versioned and replayable with DataLad-backed workflows.

## Release requirement

Public releases should demonstrate at least one benchmarked end-to-end workflow at Level 2, with an
optional Level 3 path documented for serious reproducibility use cases.
