# MRIQC Report Wrapper Summary

- Status: `succeeded`
- Derivative root: `/tmp/clawneuro-m5-work/mriqc/run-output/derivatives`
- Modalities: bold
- Telemetry disabled: `true`
- HTML reports: 2
- IQM tables: 2

## Commands
- participant: `docker run --rm -v /tmp/clawneuro-phase2-ds003020:/clawneuro/input:ro -v /tmp/clawneuro-m5-work/mriqc/run-output/derivatives:/clawneuro/output:rw -v /tmp/clawneuro-m5-work/mriqc/run-output/work:/clawneuro/work:rw nipreps/mriqc:24.0.0 /clawneuro/input /clawneuro/output participant --participant-label UTS01 --session-id 1 -m bold --nprocs 2 --omp-nthreads 2 --mem_gb 12 -w /clawneuro/work --no-sub`
- group: `docker run --rm -v /tmp/clawneuro-phase2-ds003020:/clawneuro/input:ro -v /tmp/clawneuro-m5-work/mriqc/run-output/derivatives:/clawneuro/output:rw -v /tmp/clawneuro-m5-work/mriqc/run-output/work:/clawneuro/work:rw nipreps/mriqc:24.0.0 /clawneuro/input /clawneuro/output group --session-id 1 -m bold --nprocs 2 --omp-nthreads 2 --mem_gb 12 -w /clawneuro/work --no-sub`

## Failure Notes
- none
