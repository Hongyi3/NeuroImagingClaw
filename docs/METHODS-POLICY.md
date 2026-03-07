# Methods Policy

## Core rule

Publication-facing methods text must be assembled from executed workflow metadata, fixed templates,
and tool-generated boilerplate whenever available. It must not be invented by freeform prompting.

## Allowed sources for methods text

- upstream tool boilerplate;
- executed command lines;
- recorded software versions;
- run manifests and configuration files;
- deterministic text templates maintained in the repository.

## Disallowed behavior

- inventing software versions;
- claiming a workflow step that was not executed;
- smoothing over warnings or missing metadata;
- describing a task GLM pathway when only connectivity post-processing was run;
- describing a derivative as BIDS-compliant if metadata requirements were not met.

## Manuscript-ready output requirements

Every substantial run should make it possible to render:

- a methods section;
- software citations / acknowledgements hints;
- a participant / run inventory table;
- QC and exclusion notes;
- a reproducibility appendix.

## Review policy

Methods-related PRs should be reviewed not only for wording but for traceability:

- can each sentence be traced to a manifest, metadata field, or upstream boilerplate?
- does the text preserve uncertainty and warnings?
- does the text distinguish executed steps from recommended follow-up steps?
