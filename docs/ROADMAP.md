# Roadmap

## Phase 0 — Constitution

Goal: make the project intellectually and operationally coherent before heavy implementation.

Deliverables:

- project charter;
- architecture document;
- benchmark specification;
- methods, privacy, and reproducibility policies;
- contributor and governance files;
- skill catalog and first-pass skill stubs.

Exit criteria:

- repo is understandable to external contributors;
- Codex can read a stable implementation constitution;
- milestone order is fixed.

## Phase 1 — Intake and audit

Goal: turn DICOM or messy BIDS input into an auditable, validated project state.

Deliverables:

- `bids_auditor`
- `dicom_to_bids`
- `deid_check`
- shared run manifest types
- benchmark smoke fixtures

Exit criteria:

- DICOM -> BIDS works on representative public cases;
- validator output is summarized cleanly;
- OpenNeuro-readiness checks are explicit;
- failures are actionable rather than opaque.

## Phase 2 — QC and preprocessing

Goal: convert valid BIDS input into high-trust derivatives plus inspectable QC.

Deliverables:

- `mriqc_report`
- `anat_bold_prep`
- report harvesting utilities
- container execution layer

Exit criteria:

- MRIQC and preprocessing are reproducible on benchmark datasets;
- visual reports are preserved and surfaced;
- derivative layout is correct;
- methods metadata is collected.

## Phase 3 — Analysis and reporting

Goal: make the platform paper-worthy.

Deliverables:

- `task_glm`
- `rest_connectivity`
- `report_bundle`
- `repro_bundle`

Exit criteria:

- task and rest paths are clearly split;
- outputs are publication-ready;
- methods text is deterministic;
- benchmark comparisons with baselines are working.

## Phase 4 — Diffusion

Goal: extend into diffusion MRI without diluting v1 quality.

Deliverables:

- `diffusion_prep`
- optional diffusion reconstruction wrapper
- diffusion report sections
- diffusion benchmark track

Exit criteria:

- diffusion path works through the same provenance and reporting contracts;
- benchmark evidence exists;
- documentation stays coherent.

## Phase 5 — Hardening and publication

Goal: turn the software into a citable academic project with community credibility.

Deliverables:

- DOI-backed release;
- benchmark report bundle;
- reproducible demos;
- JOSS submission package;
- field-facing methods paper outline;
- conference/tutorial material.

Exit criteria:

- public benchmark evidence is frozen for the release;
- repository hygiene is strong;
- external users can follow docs end to end.
