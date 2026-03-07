# Codex implementation sequence

## Sprint 1 — repository foundation

- create typed run manifest models
- create skill result models
- create CLI skeleton
- create report/provenance directory helpers
- create shared container execution interface
- create baseline test harness

## Sprint 2 — audit layer

- implement `bids_auditor`
- normalize validator output to machine-readable JSON
- add human-readable summary renderer
- add example fixtures and smoke tests

## Sprint 3 — intake layer

- implement `dicom_to_bids`
- support heuristic-driven conversion
- emit curation manifest and copied sidecars
- integrate post-conversion validation

## Sprint 4 — privacy layer

- implement `deid_check`
- surface structural defacing readiness
- generate export-readiness checklist
- ensure conservative wording about ethics / consent

## Sprint 5 — QC and prep

- implement `mriqc_report`
- implement `anat_bold_prep`
- preserve upstream report artifacts
- collect boilerplate and version metadata

## Sprint 6 — split downstream analysis

- implement `task_glm`
- implement `rest_connectivity`
- forbid cross-use where scientifically inappropriate
- update benchmark suite

## Sprint 7 — publication layer

- implement `report_bundle`
- implement `repro_bundle`
- render methods text from manifests
- render citation / acknowledgements hints

## Sprint 8 — diffusion

- implement `diffusion_prep`
- connect to benchmark track
- extend reporting + provenance

## Sprint 9 — hardening

- benchmark freeze
- release notes
- DOI / citation setup
- JOSS package preparation
