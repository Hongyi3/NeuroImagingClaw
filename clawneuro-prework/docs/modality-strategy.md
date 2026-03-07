# Modality Strategy

## Why the first release is narrow

Computational neuroscience is too broad for a credible v1.

A professional v1 should do one story extremely well:
1. ingest public neurophysiology data,
2. validate it against the field standard,
3. run a canonical analysis pipeline,
4. emit a reproducibility bundle,
5. reproduce at least one public computational model.

That creates a coherent narrative for users, reviewers, and papers.

## Release 0.1

### Included
- NWB
- DANDI
- extracellular ephys
- spike sorting and QC
- spike-train analytics
- model reproduction
- model portability experiments
- reproducibility bundle tooling

### Deferred
- broad human neuroimaging
- full BIDS Apps ecosystem
- mature calcium imaging lane
- large-scale workflow bridges
- generalized literature automation

## Release 0.2

### Add
- BIDS / OpenNeuro
- MNE / MNE-BIDS
- BIDS Validator integration
- human EEG / MEG / iEEG
- optional BIDS-App wrappers

## Release 0.3

### Add selectively
- calcium imaging
- workflow-system bridge
- simulator-scale portability suites
- more public reproduction packs

## Why this order matters

This sequence:
- gives the project a clean identity;
- matches the strongest existing standards ecosystems;
- avoids diffuse maintenance cost;
- supports a better JOSS / methods-paper story;
- lets benchmarks mature before the surface area expands.

