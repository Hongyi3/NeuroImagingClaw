# Containers

ClawNeuro should be container-first for heavyweight neuroimaging tools.

## Strategy

- use BIDS-App style containers whenever possible;
- prefer version-pinned upstream images;
- support Docker for local workstations;
- support Apptainer for HPC execution;
- capture image tags and digests in run manifests;
- do not hide upstream container provenance.

## Canonical mount layout

The Phase 2 wrappers use stable container paths so planned commands stay deterministic and easy to
audit:

- `/clawneuro/input` for the input BIDS dataset
- `/clawneuro/output` for the wrapped derivative output root
- `/clawneuro/work` for the wrapper-controlled work directory
- `/clawneuro/config` for mounted auxiliary config files
- `/clawneuro/license` for FreeSurfer license files when enabled
- `/clawneuro/upstream/<label>` for read-only reuse-derivative mounts

These roots are rendered directly in `ExecutionRequest.argv()` output and preserved in run
manifests rather than being hidden behind opaque abstractions.

## Notes

Some upstream tools have licensing or runtime constraints. Treat those as configuration and
documentation concerns from the beginning rather than as late surprises. The repository currently
tests request rendering for pinned MRIQC and fMRIPrep-family execution, but Docker and Apptainer
are still absent in this inspected workspace.

For M5, the default benchmark path is Docker on public `ds003020`, with Apptainer as the supported
fallback. The benchmark drivers must require an explicit `--dataset-root`; they do not fetch data
implicitly and they do not weaken the local-first privacy posture.
