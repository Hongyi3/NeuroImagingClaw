# Benchmarking

## Benchmark philosophy

Benchmarks are not a marketing extra.

In ClawNeuro they determine:
- which skills are considered core,
- which releases are credible,
- what can be claimed in papers,
- and whether the project deserves community trust.

## Benchmark layers

### CI smoke
Fast, deterministic, local or synthetic.

### nightly / scheduled
Longer-running checks, optional remote public fixtures.

### release qualification
Frozen public benchmark panel. Must pass before release.

## Benchmark tracks

## Track 1 — NWB / DANDI ingestion
Questions:
- can the skill load the data?
- can it validate schema compliance?
- can it inspect best-practice issues?
- can it emit a correct manifest and bundle?

Milestone 1 note:
- the current CI smoke path stops at routing plus bundle generation using synthetic local fixtures;
- real NWB loading and validation stay in Milestone 2.

## Track 2 — extracellular ephys
Questions:
- can the wrapper execute a standard analysis path?
- are quality metrics generated?
- are key outputs stable under fixed seeds and parameters?

## Track 3 — spike-train analytics
Questions:
- are canonical summaries produced?
- are units and time bases handled correctly?
- are visual and tabular outputs complete?

## Track 4 — model reproduction
Questions:
- can a public model be fetched or prepared reproducibly?
- can canonical traces / figures be regenerated?
- are backend and environment assumptions captured clearly?

## Track 5 — BIDS / OpenNeuro (phase 2)
Questions:
- can datasets pass validation?
- can datasets be read and written consistently?
- do BIDS derivatives and reports stay standards-compliant?

## Track 6 — provenance integrity
Questions:
- is every input checksum captured?
- are commands recorded?
- is environment state logged?
- are outputs indexed in result.json?

Current smoke implementation:
- `ARCH-001` uses `examples/synthetic/foundation_request.json` and expects `nwb-intake` to be selected deterministically;
- `REPORT-001` and `REPRO-001` validate the foundation demo and `repro-enforcer` bundle outputs with no network dependency.

## Scoring dimensions

Each benchmark entry should score:
- correctness
- validator compliance
- numerical tolerance
- runtime
- memory
- provenance completeness
- report completeness

## Acceptance policy

A skill should not be upgraded to `core` until:
- CI smoke passes
- at least one public benchmark task passes
- provenance integrity passes
- documentation is synchronized with the implementation

## Release benchmark panel

Before the first public release, freeze a small panel such as:
- one NWB/DANDI validation task
- one Allen or IBL public-data task
- one spike sorting / QC task
- one model reproduction task
- one provenance-integrity task

Keep the release panel small enough to run repeatedly and defend publicly.
