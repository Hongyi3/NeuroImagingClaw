# Data Privacy Policy

## Default posture

ClawNeuro is local-first. User data should stay on the user’s machine unless they explicitly request
an export or upload workflow.

## Scope of data handled

- DICOM directories and scanner exports
- BIDS datasets
- derivatives
- subject and session metadata
- QC reports and provenance logs

## Privacy rules

1. No silent upload of user data.
2. No network-dependent processing of private imaging data by default.
3. File access should be as narrow as possible.
4. Export-readiness checks must surface de-identification and defacing status clearly.
5. Logs and manifests should avoid unnecessary exposure of sensitive metadata.

## Open sharing readiness

A dataset is **not** “OpenNeuro-ready” unless:

- it is in BIDS format;
- structural imaging privacy requirements are addressed;
- upload-blocking validator issues are resolved or clearly surfaced;
- and the user has appropriate rights and approvals to share.

## Consent and ethics

ClawNeuro can help assess technical readiness, but it cannot certify that ethics approvals or sharing
permissions are adequate. That remains the user’s responsibility.
