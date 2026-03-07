# Tests

Current test coverage focuses on the shared foundation and Phase 1 skill contracts:

- unit tests for typed manifests, config loading, layout helpers, provenance, and reporting;
- planner tests for dataset inspection and Phase 1 handoff logic;
- contract tests for `bids_auditor`, `dicom_to_bids`, and `deid_check`;
- CLI integration tests against synthetic fixtures and dry-run skill execution.

Heavy upstream tool execution is intentionally not part of the default test suite yet. Benchmark and
container-backed regression coverage should be added as opt-in tracks once those skills land.
