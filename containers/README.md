# Containers

ClawNeuro should be container-first for heavyweight neuroimaging tools.

## Strategy

- use BIDS-App style containers whenever possible;
- prefer version-pinned upstream images;
- support Docker for local workstations;
- support Apptainer for HPC execution;
- capture image tags and digests in run manifests;
- do not hide upstream container provenance.

## Notes

Some upstream tools have licensing or runtime constraints. Treat those as configuration and
documentation concerns from the beginning rather than as late surprises.
