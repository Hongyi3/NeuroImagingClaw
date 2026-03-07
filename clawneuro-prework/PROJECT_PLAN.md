# ClawNeuro Project Plan

## 1. Positioning

ClawNeuro should be framed as **research infrastructure for computational neuroscience**.

That framing matters. If the project is presented as “ClawBio for neuroscience,” it will read like a domain fork. If it is presented as “the reference standards-native workflow and reproducibility layer for computational neuroscience,” it becomes legible to labs, standards bodies, reviewers, and funders.

### Core claim
ClawNeuro is the layer that makes computational neuroscience standards and pipelines:
- callable by agents,
- reproducible by humans,
- benchmarkable by maintainers,
- citable by the field.

## 2. The strategic wedge

The best first wedge is not “all of computational neuroscience.”

It is:

### v1
- NWB / DANDI intake and validation
- extracellular ephys analysis and QC
- spike-train analytics
- public model reproduction
- reproducibility bundles and benchmark harnesses

### v2
- BIDS / OpenNeuro human electrophysiology
- MNE / MNE-BIDS workflows
- BIDS Apps and fMRIPrep orchestration
- workflow bridges for Spyglass / DataJoint Elements
- calcium imaging production lane

This ordering is deliberate:
- it aligns with the strongest current neurophysiology standards;
- it creates a clean benchmark story early;
- it gives the project a distinctive modeling identity;
- it avoids becoming an unfocused neuroscience omnibus.

## 3. Product thesis

ClawNeuro should do **five things only**, but do them exceptionally well.

### 3.1 Discover
Detect modality, format, archive, and likely intent from files or user instructions.

### 3.2 Standardize
Convert or validate using existing field standards rather than internal ad hoc schemas.

### 3.3 Execute
Run benchmarked analysis or simulation backends through stable wrappers.

### 3.4 Explain
Produce concise, publication-grade reports, manifests, and provenance artifacts.

### 3.5 Reproduce
Emit a full bundle that another lab, a reviewer, or future-you can rerun without the original agent.

## 4. Architectural recommendation

## 4.1 Core components

### Neuro Orchestrator
Routes by:
- file type
- declared modality
- archive metadata
- task intent
- trust tier

### Skill library
Each skill is a single-responsibility, reviewable scientific unit with:
- explicit accepted inputs
- declared standards
- validators
- backends
- benchmarks
- citations
- known failure modes
- acceptance tests

### Standards layer
Adapters, not replacements, for:
- NWB / DANDI
- BIDS / OpenNeuro
- NeuroML / PyNN
- archive and simulator metadata

### Provenance layer
Universal bundle generation:
- report.md
- result.json
- figures/
- tables/
- commands.sh
- environment.yml
- hardware.json
- random_seeds.json
- checksums.sha256
- container/ metadata

### Benchmark harness
Public, deterministic tasks scored on:
- correctness
- validator compliance
- numerical stability
- provenance completeness
- runtime and memory
- report completeness

## 4.2 Execution profiles

Support three execution profiles from the start:

### local
For laptops and workstations, with cached local artifacts.

### cached-object-store
For “data-adjacent” compute on public large datasets. The artifact of record is still local metadata + remote asset references + reproducible commands.

### hpc
For schedulers and institutional compute. Standard container target should be Apptainer-compatible.

## 5. Skill roadmap

## 5.1 Core skills for release 0.1

### neuro-orchestrator
Purpose: routing, planning, report assembly, skill chaining.

### nwb-intake
Purpose: load NWB, inspect contents, validate schema and best practices, emit a machine-readable manifest.

### dandi-explorer
Purpose: search, pull, cache, summarize, and prepare public DANDI assets for downstream skills.

### spike-pipeline
Purpose: preprocessing, sorter invocation, post-processing, QC, curation summary, and standardized outputs.

### spike-train-analytics
Purpose: canonical downstream analyses on sorted units and related time series.

### repro-enforcer
Purpose: universal bundle generation with reproducibility metadata.

### model-reproducer
Purpose: run public published models and recreate canonical traces or figure panels.

### model-portability
Purpose: attempt representation and execution across portable standards and simulator backends when scientifically justified.

## 5.2 Skills for release 0.2+

### human-ephys-bids
### neuroimaging-prep
### calcium-pipeline
### workflow-bridge

## 6. Benchmark strategy

Every accepted skill must satisfy **all four** of these levels.

### Level A — unit and schema tests
Does the code work?

### Level B — tiny public or synthetic demo
Does it run deterministically in CI?

### Level C — public benchmark task
Does it produce known outputs on real data or known public models?

### Level D — release qualification
Does it pass the “frozen benchmark panel” selected for release approval?

### Benchmark tracks
1. NWB/DANDI ingestion and validation
2. public neurophysiology workflow execution
3. model reproduction
4. BIDS/OpenNeuro phase-2 validation
5. bundle and provenance integrity

## 7. Governance

ClawNeuro should launch with governance that assumes outside contributors will arrive.

### Trust tiers
- **core** — maintained by project maintainers; release-blocking quality bar
- **reviewed-community** — accepted after review and benchmark coverage
- **experimental** — visible but explicitly unstable and not routed by default

### Roles
- lead maintainer
- modality maintainers
- benchmark maintainer
- release manager
- documentation / publication maintainer

### Review requirement
No core skill merges without:
- benchmark entry
- tests
- demo
- citations
- explicit failure modes
- reproducibility bundle definition

## 8. Publication and influence plan

### Phase A — technical report / preprint
Goal: define the architecture and benchmark philosophy.

### Phase B — stable open-source release
Archive via Zenodo, expose GitHub citation metadata, clean release notes.

### Phase C — JOSS submission
Once documentation, tests, release engineering, and research significance are clear.

### Phase D — domain paper
A methods / software paper focused on:
- standards-native orchestration,
- benchmarked public-data workflows,
- model reproducibility,
- interoperability story.

### Phase E — community visibility
Tutorials, workshops, and conference demos.

## 9. What not to do

Do not:
- build a vague neuroscience chatbot first;
- invent a new metadata schema when a field standard exists;
- let LLM prose decide scientific thresholds or parameters;
- launch with every modality at once;
- accept unbenchmarked community skills into the core routing path;
- compete directly with NWB, BIDS, SpikeInterface, MNE, Spyglass, or simulators.

## 10. Bottom line

The winning version of this project is:

> a standards-native, benchmark-first, reproducibility platform for open neurophysiology and public model reproduction, with agent-friendly interfaces and publication-grade software discipline.

That is the version most likely to become:
- useful in real labs,
- citable in real papers,
- extensible by the community,
- respected as academic infrastructure.

