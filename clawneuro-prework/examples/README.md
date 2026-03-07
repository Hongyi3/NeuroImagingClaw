# Examples

Use this directory for:
- tiny synthetic fixtures,
- miniature public fixtures that are safe to vendor,
- expected output snapshots.

Do not place large public datasets here.

Recommended layout:
```text
examples/
├── synthetic/
├── miniature-public/
└── expected/
```

Milestone 1 fixtures now include:
- `synthetic/foundation_request.json` and `synthetic/session_stub.nwb` for deterministic routing smoke checks
- `synthetic/repro_seed_report.md` and `synthetic/repro_seed_result.json` for reproducibility bundle smoke checks
