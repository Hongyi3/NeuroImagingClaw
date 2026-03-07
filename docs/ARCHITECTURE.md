# Architecture

## Top-level design

ClawNeuro mirrors the strongest parts of ClawBio’s design:

- standalone skills;
- a routing orchestrator;
- unified reporting;
- reproducibility export;
- agent-readable project metadata.

The difference is that every major boundary is anchored to neuroimaging standards.

## Layers

### 1. Intake and curation

Responsibilities:

- receive DICOM or BIDS input;
- convert to NIfTI / BIDS when needed;
- validate metadata completeness;
- record curation provenance.

Planned skills:

- `dicom_to_bids`
- `bids_auditor`
- `deid_check`

### 2. Execution orchestration

Responsibilities:

- inspect input state;
- choose appropriate skills;
- chain outputs;
- maintain run manifests;
- assemble cross-skill reporting.

The orchestrator may plan and route but must never replace the scientific logic inside a skill.

### 3. Domain execution skills

Responsibilities:

- wrap trusted upstream neuroimaging tools;
- normalize configuration;
- collect outputs;
- expose clear contracts.

Planned skills:

- `mriqc_report`
- `anat_bold_prep`
- `task_glm`
- `rest_connectivity`
- `diffusion_prep`

### 4. Reporting and provenance

Responsibilities:

- collect upstream HTML / QC artifacts;
- generate a run dossier;
- synthesize deterministic methods text;
- export machine-readable and human-readable reproducibility files.

Planned skills:

- `report_bundle`
- `repro_bundle`

## Core repository structure

```text
clawneuro/
  src/clawneuro/
    core/
    orchestrator/
    reporting/
    provenance/
    cli/
  skills/
  benchmarks/
  docs/
  prompts/
  containers/
  tests/
```

## Execution contract for every skill

Each skill must define:

- accepted input states;
- validation logic;
- wrapped upstream tools;
- exact outputs produced;
- required provenance files;
- machine-readable result schema;
- failure classes and recovery suggestions.

## Output contract

A successful run should produce a directory with at least:

```text
run-output/
  report/
  manifests/
  logs/
  provenance/
  derivatives/   # if the skill claims BIDS-derivative outputs
```

Where applicable, derivative outputs must remain understandable without the original raw data being
co-distributed.

## Reporting contract

The reporting layer is a first-class subsystem, not decoration.

Every meaningful run should emit:

- executive summary;
- run metadata;
- upstream report links;
- warnings and QC flags;
- exact commands;
- software versions;
- container digests when containers were used;
- methods text;
- bibliography / acknowledgements hints;
- machine-readable manifest.

## Provenance contract

Minimum provenance bundle:

- `commands.sh`
- `environment.yml` or lockfile equivalent
- `checksums.sha256`
- `analysis_log.md`
- `run-manifest.json`

Preferred extended provenance:

- container image references and digests
- DataLad provenance metadata
- input and output inventories
- links to the exact BIDS derivative dataset descriptions

## Key design decisions

### Split task GLM from resting-state connectivity

After preprocessing, task and rest must diverge:

- task data -> `task_glm`
- rest / pseudo-rest -> `rest_connectivity`

This avoids forcing an inappropriate “one downstream path fits all” model.

### Wrap instead of rebuild

ClawNeuro adds:

- contracts,
- orchestration,
- provenance,
- standardized reporting,
- benchmarkability,
- agent usability.

It should not attempt to re-implement established preprocessing methods unless there is a clear,
evidence-backed reason.
