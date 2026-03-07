# Test Strategy

## Summary

Testing should prove contract stability first, then wrapped-tool fidelity. Heavy neuroimaging tools do
not belong in the default developer loop until the shared contract layer is stable.

## Test matrix

### Unit tests

Targets:
- core models and enum validation
- config loading from YAML/JSON/TOML
- run-directory layout helpers
- provenance checksum and manifest writing
- deterministic reporting and methods rendering
- orchestration planning logic

Goal:
- prove that ClawNeuro’s internal contracts are typed, stable, and deterministic.

### Contract tests

Targets:
- `bids_auditor`
- `dicom_to_bids`
- `deid_check`

Assertions:
- accepted and rejected input states
- emitted artifact paths and file formats
- warnings/blockers for incomplete states
- minimum provenance bundle files
- stable manifest serialization

### CLI integration tests

Targets:
- `plan`
- `bids-auditor`
- `dicom-to-bids`
- `deid-check`
- `report-bundle`

Goal:
- verify that CLI entry points stay aligned with the runtime packages and typed models.

### Benchmark and upstream execution tests

Status:
- not part of the default suite yet

Future targets:
- validator execution against real BIDS Validator JSON
- DICOM conversion smoke tests on public examples
- benchmark regression tracks defined in `docs/BENCHMARK-SPEC.md`

Goal:
- prove fidelity to upstream tools without making CI too heavy for routine work.

## Fixture policy

- keep default fixtures local, synthetic, and small;
- prefer filename/metadata fixtures over bulky imaging payloads for contract tests;
- add public benchmark subsets only when version-pinned and acceptance-scoped;
- never substitute smoke fixtures for scientific benchmark evidence.

## Quality gates

- new shared-core behavior requires unit tests;
- new or changed skill contracts require contract tests and fixture updates;
- output-contract changes require docs updates in the same patch;
- benchmark-affecting behavior requires a benchmark note or fixture rationale;
- heavy upstream execution should stay opt-in until pinned runtimes exist.
