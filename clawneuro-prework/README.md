# ClawNeuro

**ClawNeuro** is a standards-native, benchmark-first, reproducibility-first skill library for computational neuroscience.

It is intentionally positioned as a **sister project to ClawBio**, not a neuroscience-themed fork with a few wrappers. The goal is to preserve the parts of ClawBio that matter most—self-contained skills, an orchestrator, local-first execution, reproducibility bundles, and AI-agent-facing repository structure—while replacing the substrate with the standards, validators, archives, and benchmarked workflows that computational neuroscience actually uses.

## Thesis

The project should optimize for one outcome:

> Every neural recording and every reusable computational model should be one command away from standardization, validation, analysis, benchmarking, and publication-ready reproduction.

That makes ClawNeuro:
- infrastructure, not a chatbot;
- an execution and reproducibility layer, not a replacement for domain libraries;
- a field-facing academic software project, not a one-off lab repo.

## v1 Scope

### Primary v1 wedge
- **NWB / DANDI** intake, validation, summarization, and dataset cards
- **Extracellular electrophysiology** preprocessing, spike sorting, QC, and report generation
- **Spike-train analytics** for canonical downstream summaries
- **Computational model reproduction** across public models using NEURON / Brian2 / NEST where applicable
- **Reproducibility bundles** as a mandatory output for every skill

### Deliberately deferred to phase 2
- BIDS / OpenNeuro human EEG / MEG / iEEG
- fMRI preprocessing and derivatives orchestration
- full calcium-imaging production support
- large workflow-system bridges beyond thin interoperability adapters

## Non-negotiables

1. **Standards-native**
   - NWB / DANDI first
   - BIDS / OpenNeuro next
   - NeuroML / PyNN / ModelDB / Open Source Brain for model portability and sharing

2. **Integrate, do not reimplement**
   - Use best-in-class backends such as NeuroConv, PyNWB, NWB Inspector, SpikeInterface, Elephant, MNE, MNE-BIDS, NEURON, Brian2, NEST, NeuroML, and PyNN.
   - ClawNeuro should orchestrate, validate, benchmark, and report.

3. **Reproducibility by default**
   - Every skill should emit a reproducibility bundle, not merely claim reproducibility in the README.

4. **Benchmark-first**
   - Skills enter the core catalog only when they pass deterministic tests and public benchmark tasks.

5. **Agent-ready**
   - The repo should be legible to humans and to coding agents from day one.

## Repository map

```text
clawneuro-prework/
├── README.md
├── PROJECT_PLAN.md
├── AGENTS.md
├── llms.txt
├── clawneuro.py
├── pyproject.toml
├── docs/
├── skills/
├── templates/
├── benchmarks/
├── papers/
├── examples/
├── scripts/
├── containers/
├── src/clawneuro/
└── .github/
```

## Start here

1. Read `PROJECT_PLAN.md`
2. Read `docs/architecture.md`
3. Read `docs/codex-implementation-brief.md`
4. Read `AGENTS.md`
5. Run:

```bash
python clawneuro.py list
python clawneuro.py route --query "Inspect this NWB file" --input examples/synthetic/session_stub.nwb --json
python clawneuro.py demo foundation --output outputs/foundation-demo
python scripts/generate_catalog.py
python scripts/validate_benchmarks.py
```

If your workstation exposes the Python 3.11+ interpreter as `python3` rather than `python`, use that interpreter consistently for the commands above.

## What this scaffold is for

This repository is **prework**: a professional starting point that makes it easy for Codex (or another coding agent) to finish the real implementation without drifting away from the research-infrastructure thesis.

The scaffold includes:
- project thesis and roadmap;
- governance and publication strategy;
- AI-agent instructions;
- a neuroscience-specific skill template;
- initial core skill specs;
- benchmark and container scaffolding;
- executable foundation routing and reproducibility tooling.

## Success criteria

ClawNeuro should be considered on track only when it can do all three of these well:

1. Convert, validate, analyze, and package public neurophysiology data through standard workflows.
2. Reproduce a small set of canonical public models with one command and auditable outputs.
3. Produce benchmarkable, citable, publication-ready software artifacts.
