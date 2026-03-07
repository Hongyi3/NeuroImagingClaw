# Security Policy

ClawNeuro handles potentially sensitive neuroimaging data. Its security posture is therefore conservative.

## Threat model

- accidental data disclosure;
- over-broad filesystem access;
- silent network egress;
- unpinned containers or supply-chain drift;
- malicious or unsafe community skills;
- provenance gaps that make review impossible.

## Current security posture

- local-first by default;
- no automatic user-data upload;
- least-privilege filesystem scope;
- container-first execution for heavyweight pipelines;
- pinned versions and digests where possible;
- explicit logging of executed commands;
- no auto-installation of unreviewed third-party skills.

## Reporting vulnerabilities

Until a dedicated security contact exists, create a private reporting process before announcing production use.
Do not disclose exploitable issues in public issues until maintainers confirm a remediation plan.

## Hard requirements for future releases

- dependency review in CI;
- secret scanning;
- OpenSSF Scorecard monitoring;
- published release notes with security-impacting changes called out;
- clear rules for networked features and telemetry.
