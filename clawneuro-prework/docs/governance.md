# Governance

## Governance objective

Operate this repository like long-lived research software, not like a personal code drop.

## Maintainer structure

Recommended roles:
- project lead
- modality maintainers
  - ephys
  - models
  - human electrophysiology
  - imaging
- benchmark maintainer
- release manager
- docs / publication maintainer

## Review model

### Core skills
Require:
- two reviews where feasible
- benchmark coverage
- demo path
- catalog accuracy
- provenance definition

### Reviewed-community skills
Require:
- one substantive review
- tests
- benchmark or fixture coverage
- explicit trust tier

### Experimental skills
Can merge behind clear labels, but:
- no silent routing
- no marketing claims
- no release-blocking expectations

## Standards policy

When a contribution needs “new metadata” or “a new schema,” the default assumption should be:

1. use the existing standard correctly;
2. use an extension mechanism if the ecosystem provides one;
3. only create project-local metadata as a last resort, and namespace it clearly.

## Change management

Use repository discussions and design docs for:
- new architecture decisions
- benchmark changes
- release-scope changes
- proposed standard extensions or custom metadata

## Authorship and credit

Track substantial contributions explicitly:
- code
- benchmarks
- docs
- reproduction packs
- scientific methodology
- release engineering

Prepare for:
- `CITATION.cff`
- DOI-backed releases
- RRID registration when stable
- paper authorship criteria before submission

## Release discipline

Each public release should have:
- changelog
- benchmark status
- known limitations
- container notes
- DOI archive
- citation instructions

