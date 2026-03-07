# Benchmarks

This directory defines the benchmark panel that determines whether ClawNeuro can make strong scientific and software claims.

## Principles

- CI smoke tests should be deterministic and network-free.
- Release qualification should include pinned public fixtures.
- Every core skill should map to at least one benchmark.
- Public benchmark targets must be versioned or pinned before release claims are made.

## Recommended public benchmark sources

### NWB / DANDI
Use stable public NWB assets and Dandisets, pinned by identifier and version before release.

### Allen / IBL
Use one carefully selected public dataset family for release qualification, not an expanding collection of ad hoc examples.

### BIDS / OpenNeuro
Use `bids-examples` for structural smoke tests and one pinned public OpenNeuro example for release qualification.

### Models
Use one or a few well-known public models with clearly identified reference outputs.

## Policy

A benchmark claim in docs or papers should only be made if the corresponding manifest entry is:
- versioned,
- reproducible,
- and still passing on the relevant release tag.

