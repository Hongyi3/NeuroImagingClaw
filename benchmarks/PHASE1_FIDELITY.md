# Phase 1 Fidelity Notes

These notes record the checked-in Phase 1 evidence for the intake and audit wrappers. They are not
a substitute for a frozen release benchmark suite, but they do anchor the wrappers to real public
interfaces and public reference data.

## BIDS Validator fidelity

- Source dataset: `bids-examples/ds005`
- Source commit: `8bb0cdd090e25180ee2f0d35b02bb45a1fb49e2b`
- Tool: `bids-validator-deno 2.4.1`
- Stored artifact: `tests/fixtures/fidelity/bids_validator/ds005_validator_v241_excerpt.json`
- Stored artifact SHA256: `ee74b88e8344903141f64246a834651046c69c14eced997495185dbd5b725df2`
- Command used:

```bash
bids-validator-deno /tmp/bids-examples/ds005 \
  --format json \
  --ignoreNiftiHeaders \
  --config /tmp/config.json
```

- Outcome:
  The current validator JSON shape uses `issues.issues[*].severity`, `issueMessage`, and
  `summary.schemaVersion`. ClawNeuro normalizes that current shape in addition to the older
  `issues.errors` and `issues.warnings` shape.
- Limitation:
  Only a small excerpt of the public validator output is checked in for tests. The full dataset
  output is not vendored into the repository.

## Public DICOM-to-BIDS execution evidence

- Source dataset: `neurolabusc/dcm_qa_nih`
- Source commit: `d302d6e241dda747b79ee1724ada3200179755a2`
- Source archive URL:
  `https://codeload.github.com/neurolabusc/dcm_qa_nih/tar.gz/d302d6e241dda747b79ee1724ada3200179755a2`
- Source archive SHA256: `585df8757ada1e4121d50daa8114c991983aba63e2568fe5fbc2bfe62ce561c2`
- Upstream tutorial/tooling reference: `UNFmontreal/Dcm2Bids` commit
  `77845ab91174a675bd8079c465728ba7bc3a7de1`
- Checked-in evidence root: `benchmarks/artifacts/phase1_dcm_qa_nih/`
- Pinned runtime packages used:
  - `dcm2bids 3.2.0`
  - `dcm2niix 1.0.20250506` package, self-reported runtime string
    `Chris Rorden's dcm2niiX version v1.0.20250505  Clang17.0.0 ARM (64-bit MacOS)`
  - `bids-validator-deno 2.4.1`
- Reproduction command:

```bash
python3.14 -m venv /tmp/clawneuro-m3
/tmp/clawneuro-m3/bin/pip install -e '.[dev]' dcm2bids==3.2.0 dcm2niix==1.0.20250506 bids-validator-deno==2.4.1
/tmp/clawneuro-m3/bin/python benchmarks/run_phase1_public_dicom_to_bids.py \
  --workspace /tmp/clawneuro-m3-work \
  --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih
```

- Outcome:
  - `dicom_to_bids` completed with `status: succeeded`.
  - Runtime evidence captured resolved executables and version strings for `dcm2bids`,
    `dcm2niix`, and `bids-validator-deno`.
  - Post-conversion validation completed successfully and the checked-in run manifest reports
    `modalities: ["bold", "fmap"]`.
  - The wrapper now synthesizes a minimum `dataset_description.json` when upstream curation omits
    it and removes upstream `tmp_dcm2bids` output before validation so the curated BIDS tree can
    be validated cleanly.
- Stored evidence:
  - `benchmarks/artifacts/phase1_dcm_qa_nih/benchmark-metadata.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/manifests/conversion-manifest.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/manifests/run-manifest.json`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/provenance/commands.sh`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/provenance/checksums.sha256`
  - `benchmarks/artifacts/phase1_dcm_qa_nih/report/conversion-report.md`
- Limitation:
  The raw benchmark dataset is not vendored into the repository; reruns fetch the pinned public
  archive and then regenerate the checked-in manifests, reports, and provenance bundle.
