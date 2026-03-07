# Security Policy

## Supported versions

This repository is pre-release. Security support applies to the default branch and the latest tagged release.

## Reporting a vulnerability

Please do **not** open a public issue for a suspected vulnerability.

Instead:
- email the maintainers directly, or
- use GitHub private vulnerability reporting once enabled.

Include:
- affected component
- reproduction steps
- impact assessment
- suggested mitigation, if known

## Security priorities

The highest-priority concerns for this project are:
- unintended data exfiltration
- unsafe handling of local research data
- supply-chain risk in workflow wrappers
- unreviewed execution paths in community skills
- insecure CI or release workflows

## Operational policy

- keep network access explicit
- avoid storing secrets in code or tests
- use least-privilege defaults
- review workflow and release files carefully
- protect `.github/workflows` with CODEOWNERS

