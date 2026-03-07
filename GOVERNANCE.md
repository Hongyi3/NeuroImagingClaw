# Governance

ClawNeuro is governed as open scientific infrastructure.

## Principles

1. Standards before novelty.
2. Reuse before reinvention.
3. Transparency before convenience.
4. Public benchmark evidence before strong performance claims.
5. Community interoperability before ecosystem lock-in.

## Maintainer roles

- **Project leads**: overall architecture, roadmap, releases.
- **Domain maintainers**: one or more maintainers per skill.
- **Methods reviewers**: review scientific validity and reporting.
- **Benchmark maintainers**: curate datasets, acceptance criteria, and regression monitoring.
- **Docs maintainers**: maintain charter, guides, and publication artifacts.

## Decision process

- Small changes: normal review through pull requests.
- Architectural changes: documented in `docs/` with rationale and migration path.
- Governance changes: issue + discussion + explicit maintainer approval.

## Release philosophy

A release is considered legitimate only when:

- benchmark evidence is current,
- documentation is synced,
- reproducibility artifacts are still valid,
- and no core contract has been silently weakened.

## External advisory circle

The project should recruit a small external advisory circle drawn from:

- BIDS / BIDS Apps contributors;
- NiPreps / PennLINC style tool maintainers;
- open-science and reproducibility practitioners;
- lab PIs or research software engineers who can evaluate adoption realism.
