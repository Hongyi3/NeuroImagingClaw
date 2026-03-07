# Project Charter

## Working name

**ClawNeuro**

## Mission

Build a BIDS-native, local-first, glass-box orchestration layer for neuroimaging that turns trusted
tools and standards into auditable skills with publication-ready outputs.

## Why this project should exist

Neuroimaging already has strong standards and excellent tools, but labs still face a recurrent gap:

- DICOM-to-BIDS curation is fragile.
- Validation and de-identification checks are inconsistently enforced.
- QC, preprocessing, and downstream analysis are scattered across tools.
- Provenance and methods reporting are often afterthoughts.
- Reproducing a figure or a methods section remains harder than it should be.

ClawNeuro should address that orchestration gap without replacing the underlying scientific engines.

## Product promise

**Input**

- a DICOM directory, scanner export, or an existing BIDS dataset.

**Process**

- curate or validate;
- check privacy / export readiness;
- run QC;
- preprocess;
- optionally model task data or derive resting-state connectivity outputs;
- assemble report and provenance bundles.

**Output**

- BIDS-compliant derivatives;
- upstream visual reports plus a unified dossier;
- deterministic methods text;
- machine-readable manifests;
- exact rerun instructions.

## Scientific contract

1. No custom science outside standards unless explicitly labeled experimental.
2. No result without provenance.
3. No claimed derivative without the required BIDS derivative metadata.
4. No publication-facing report without exact versions and workflow traceability.
5. No AI-generated scientific claim unless it can be traced to executed outputs or metadata.

## Scope

### Version 1

- structural MRI (T1w / T2w)
- BOLD fMRI
- DICOM-to-BIDS intake
- BIDS validation
- de-identification readiness checks
- MRIQC
- fMRIPrep-based preprocessing
- task GLM from derivatives
- resting-state connectivity post-processing
- unified reporting and reproducibility

### Version 1.1

- diffusion MRI preprocessing
- diffusion reconstruction pathway
- harder benchmark suites
- stronger methods-paper package

### Later

- EEG / MEG through MNE-BIDS
- PET / ASL and broader multimodal workflows
- richer study-level project management and cohort summaries

## Non-goals

- clinical diagnosis or decision support;
- replacing upstream pipelines;
- building a new data standard;
- supporting every modality at launch;
- optimizing for prompt-only usage over reproducible execution.

## Success criteria

A first public release is successful when:

- an external lab can use it without direct maintainer intervention;
- public benchmark evidence exists;
- outputs are auditable and manuscript-ready;
- the repository is citable and reviewable;
- and the project can credibly support a JOSS submission.
