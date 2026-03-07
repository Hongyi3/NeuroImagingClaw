# Phase 2 QC and Preprocessing Benchmark Path

## Status

As of March 7, 2026, this repository contains the M5 benchmark harness for public `ds003020`, but
it does **not** yet contain checked-in live artifact trees for MRIQC or fMRIPrep-family
preprocessing. The inspected workspace lacked `docker`, `apptainer`, `mriqc`, and `fmriprep`, so
the live execution step remains blocked and must be completed in a separate reproducible
environment.

## Target dataset and scope

- Dataset: `ds003020`
- Participant: `01`
- Scope:
  - MRIQC with `anat` and `bold` modalities plus the explicit group-level pass
  - anat/BOLD preprocessing with `--output-layout bids`
  - FreeSurfer disabled for the baseline benchmark path

## Pinned container references

- MRIQC:
  - Docker: `nipreps/mriqc:24.0.0`
  - Apptainer: `docker://nipreps/mriqc:24.0.0`
- fMRIPrep-family preprocessing:
  - Docker: `nipreps/fmriprep:23.1.2`
  - Apptainer: `docker://nipreps/fmriprep:23.1.2`

## Exact benchmark commands

```bash
python3.14 -m venv /tmp/clawneuro-m5
/tmp/clawneuro-m5/bin/pip install -e '.[dev]'
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_mriqc.py \
  --dataset-root <ds003020_root> \
  --workspace /tmp/clawneuro-m5-work/mriqc \
  --artifact-root benchmarks/artifacts/phase2_ds003020_mriqc \
  --backend docker
/tmp/clawneuro-m5/bin/python benchmarks/run_phase2_public_anat_bold_prep.py \
  --dataset-root <ds003020_root> \
  --workspace /tmp/clawneuro-m5-work/prep \
  --artifact-root benchmarks/artifacts/phase2_ds003020_anat_bold_prep \
  --backend docker
```

Apptainer is the supported fallback when Docker is unavailable.

## Preserved outputs required from a live run

- MRIQC:
  - run manifest and summary manifest
  - participant/group stdout and stderr logs
  - provenance bundle
  - preserved HTML reports
  - preserved IQM tables
  - derivative `dataset_description.json`
- anat/BOLD preprocessing:
  - run manifest and summary manifest
  - stdout and stderr logs
  - provenance bundle
  - preserved HTML reports
  - preserved confounds TSV/JSON files
  - preserved boilerplate files from `logs/`
  - derivative `dataset_description.json`

## What the eventual live evidence will prove

- One public `ds003020` MRIQC path and one public `ds003020` anat/BOLD preprocessing path execute
  successfully through ClawNeuro's wrappers.
- The wrappers preserve upstream reports, IQM/confounds tables, derivative metadata, and
  boilerplate in machine-readable manifests.
- Container runtime and image identifiers are recorded explicitly rather than assumed.

## What it will not prove

- scientific superiority over upstream tools;
- clinical validity or diagnostic suitability;
- downstream task GLM or resting-state correctness;
- FreeSurfer-enabled reproducibility;
- robustness across multiple public datasets.

## Remaining risks

- The baseline preprocessing benchmark keeps FreeSurfer disabled to avoid license/environment
  variance during the first live evidence pass.
- A single public dataset is a milestone exit path, not a full benchmark freeze.
- The copied benchmark artifact trees should remain limited to manifests, logs, provenance files,
  reports, and selected preserved derivative evidence rather than the raw benchmark dataset.
