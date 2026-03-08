# Anatomical and BOLD Preprocessing Summary

- Status: `failed`
- Derivative root: `/tmp/clawneuro-m5-work/prep/run-output/derivatives`
- Output spaces: MNI152NLin2009cAsym:res-2
- FreeSurfer enabled: `false`
- Preserved HTML reports: 0
- Preserved boilerplate files: 0
- Preserved confounds files: 0

## Command
`docker run --rm -v /tmp/clawneuro-phase2-ds003020:/clawneuro/input:ro -v /tmp/clawneuro-m5-work/prep/run-output/derivatives:/clawneuro/output:rw -v /tmp/clawneuro-m5-work/prep/run-output/work:/clawneuro/work:rw nipreps/fmriprep:23.1.2 /clawneuro/input /clawneuro/output participant --participant-label UTS01 --output-layout bids --output-spaces MNI152NLin2009cAsym:res-2 --work-dir /clawneuro/work --notrack --fs-no-reconall --nprocs 2 --omp-nthreads 2 --mem-mb 12000`

## Failure Notes
- none
