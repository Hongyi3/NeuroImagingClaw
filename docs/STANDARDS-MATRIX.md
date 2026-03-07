# Standards Matrix

| Area | Standard / tool family | Role in ClawNeuro | Planned status |
|---|---|---|---|
| Dataset organization | BIDS | Canonical input organization and metadata model | v1 |
| Validation | BIDS Validator / schema | Input and derivative compliance checks | v1 |
| DICOM conversion | dcm2niix | NIfTI + sidecar generation | v1 |
| DICOM curation | HeuDiConv / Dcm2Bids | BIDS curation heuristics | v1 |
| Dataset query | PyBIDS | Internal indexing, discovery, and model support | v1 |
| Statistical model spec | BIDS Stats Models | Machine-readable task analysis specs | v1 |
| Task model execution | FitLins / Nilearn | First-level task analysis from derivatives | v1 |
| QC | MRIQC | Image quality metrics and reports | v1 |
| Structural + BOLD prep | fMRIPrep | Standard preprocessing backbone | v1 |
| Resting-state postproc | XCP-D | Connectivity-oriented postprocessing | v1 |
| Diffusion prep | QSIPrep | Diffusion preprocessing backbone | v1.1 |
| Diffusion recon | QSIRecon | Reconstruction workflows | v1.1 |
| Templates / atlases | TemplateFlow | Programmatic template and atlas access | v1 |
| Provenance | DataLad | High-end rerun and archival provenance | optional v1 |
| EEG / MEG future | MNE-BIDS | Future electrophysiology branch | future |
| Container execution | BIDS Apps / Docker / Apptainer | Portable pipeline execution | v1 |
| Reports | NiPreps-style reports / NiReports | Inspectable QC and report components | v1 |

## Interpretation

This matrix is the answer to “what are we actually building?”

We are building:

- contracts,
- orchestration,
- provenance,
- reporting,
- and agent usability

on top of this standards stack.
