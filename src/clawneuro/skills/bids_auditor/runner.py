"""Runner for the BIDS auditor skill."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    CommandRecord,
    ExecutionBackend,
    ExecutionRequest,
    InputDatasetKind,
    InvalidInputStateError,
    RunStatus,
    SkillDescriptor,
    SkillKind,
    SkillResult,
    SoftwareInventoryRecord,
    WarningRecord,
    WarningSeverity,
    ensure_run_layout,
    execute_request,
    inspect_bids_dataset,
    planned_command_record,
)
from clawneuro.core.config import write_model_json
from clawneuro.core.bids import detect_input_state
from clawneuro.core.models import ClawBaseModel, ProvenanceRecord
from clawneuro.reporting import render_markdown_report
from clawneuro.reporting.models import ReportBundleDraft, ReportSection
from clawneuro.skills.bids_auditor.config import BidsAuditorConfig
from clawneuro.skills.common import finalize_skill_result


class ValidatorIssue(ClawBaseModel):
    """Normalized validator issue."""

    code: str
    severity: WarningSeverity
    category: str
    message: str
    location: Optional[str] = None


class ValidatorSummary(ClawBaseModel):
    """Machine-readable validator summary."""

    status: RunStatus
    errors: int = 0
    warnings: int = 0
    issues: List[ValidatorIssue] = Field(default_factory=list)
    raw_source: str = "planned"


def _issue_category(issue: Mapping[str, Any]) -> str:
    code = str(issue.get("code", "")).lower()
    message = str(issue.get("reason", "") or issue.get("message", "")).lower()
    if "json" in code or "metadata" in code or "metadata" in message:
        return "metadata"
    if "subject" in code or "structure" in code or "folder" in message:
        return "structure"
    return "general"


def normalize_validator_output(raw: Mapping[str, Any], status: RunStatus) -> ValidatorSummary:
    """Normalize common BIDS validator JSON shapes."""

    issues_section = raw.get("issues", {})
    errors = issues_section.get("errors", []) if isinstance(issues_section, Mapping) else []
    warnings = issues_section.get("warnings", []) if isinstance(issues_section, Mapping) else []
    normalized_issues: List[ValidatorIssue] = []
    for raw_issue in list(errors) + list(warnings):
        if not isinstance(raw_issue, Mapping):
            continue
        severity = WarningSeverity.ERROR if raw_issue in errors else WarningSeverity.WARNING
        normalized_issues.append(
            ValidatorIssue(
                code=str(raw_issue.get("code", "validator-issue")),
                severity=severity,
                category=_issue_category(raw_issue),
                message=str(raw_issue.get("reason", "") or raw_issue.get("message", "Validator issue")),
                location=str(raw_issue.get("location")) if raw_issue.get("location") else None,
            )
        )

    return ValidatorSummary(
        status=status,
        errors=len(errors),
        warnings=len(warnings),
        issues=normalized_issues,
        raw_source=str(raw.get("source", "validator-json")),
    )


def build_validator_request(config: BidsAuditorConfig) -> ExecutionRequest:
    """Create the validator execution request for the chosen backend."""

    args = [str(config.bids_root), "--json"]
    if config.participant_labels:
        args.extend(["--participant-label"] + config.participant_labels)
    return ExecutionRequest(
        name="bids-validator",
        backend=config.backend,
        executable=config.validator_executable,
        args=args,
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        description="Validate a BIDS dataset and emit machine-readable JSON.",
    )


def _render_audit_report(summary: ValidatorSummary, inventory_name: str) -> ReportBundleDraft:
    body = "\n".join(
        [
            "Validator status: `{0}`".format(summary.status.value),
            "Errors: {0}".format(summary.errors),
            "Warnings: {0}".format(summary.warnings),
        ]
    )
    if summary.issues:
        body = body + "\n\nIssue categories: " + ", ".join(
            sorted({issue.category for issue in summary.issues})
        )
    return ReportBundleDraft(
        title="BIDS Audit Report: {0}".format(inventory_name),
        sections=[ReportSection(title="Validation Summary", body=body)],
        warnings=[
            WarningRecord(
                code=issue.code,
                severity=issue.severity,
                message=issue.message,
                hint=issue.location,
            )
            for issue in summary.issues
        ],
        artifact_index={},
    )


def _render_triage_checklist(summary: ValidatorSummary) -> str:
    lines = ["# BIDS Triage Checklist", ""]
    if not summary.issues:
        lines.append("- No validator issues were recorded.")
        return "\n".join(lines) + "\n"
    for issue in summary.issues:
        lines.append(
            "- [{0}] {1}: {2}".format(issue.severity.value, issue.category, issue.message)
        )
    return "\n".join(lines) + "\n"


def run_bids_auditor(config: BidsAuditorConfig) -> SkillResult:
    """Plan or execute BIDS validation and emit a manifest-backed result."""

    input_state = detect_input_state(config.bids_root)
    if input_state.kind not in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        raise InvalidInputStateError(
            "bids_auditor requires a BIDS dataset root.",
            context={"path": str(config.bids_root), "detected_kind": input_state.kind.value},
        )

    inventory = inspect_bids_dataset(config.bids_root)
    layout = ensure_run_layout(config.output_root)
    validator_request = build_validator_request(config)
    command_record: CommandRecord
    raw_validator_output: Dict[str, Any]
    warnings: List[WarningRecord] = []

    stdout_path = layout.logs_dir / "bids-validator.stdout.log"
    stderr_path = layout.logs_dir / "bids-validator.stderr.log"
    if config.execute:
        command_record = execute_request(validator_request, stdout_path=stdout_path, stderr_path=stderr_path)
        try:
            raw_validator_output = json.loads(stdout_path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            raw_validator_output = {"issues": {}, "source": "validator-stdout-unparseable"}
            warnings.append(
                WarningRecord(
                    code="validator-json-unparseable",
                    severity=WarningSeverity.ERROR,
                    message="BIDS Validator output could not be parsed as JSON.",
                    hint="Inspect the validator stdout log.",
                )
            )
        status = command_record.status
    else:
        command_record = planned_command_record(validator_request)
        raw_validator_output = {"issues": {"errors": [], "warnings": []}, "source": "planned"}
        status = RunStatus.PLANNED
        warnings.append(
            WarningRecord(
                code="validator-not-executed",
                severity=WarningSeverity.INFO,
                message="Validator command was planned but not executed.",
                hint="Re-run with execute=True when the validator is installed.",
            )
        )

    summary = normalize_validator_output(raw_validator_output, status=status)
    validator_summary_path = write_model_json(layout.manifests_dir / "validator-summary.json", summary)
    audit_bundle = _render_audit_report(summary, inventory.dataset_name)
    audit_report_path = layout.report_dir / "audit-report.md"
    audit_report_path.write_text(render_markdown_report(audit_bundle), encoding="utf-8")
    triage_path = layout.report_dir / "triage-checklist.md"
    triage_path.write_text(_render_triage_checklist(summary), encoding="utf-8")

    warnings.extend(audit_bundle.warnings)

    result = SkillResult(
        skill=SkillDescriptor(
            name="bids_auditor",
            kind=SkillKind.AUDIT,
            version=__version__,
            contract_path=Path("skills/bids_auditor/SKILL.md"),
        ),
        status=status,
        summary=(
            "Validated BIDS structure and produced a normalized audit summary."
            if status == RunStatus.SUCCEEDED
            else "Planned BIDS validation and emitted a manifest-backed audit scaffold."
        ),
        input_state=input_state,
        dataset_inventory=inventory,
        warnings=warnings,
        artifacts=[
            ArtifactRecord(
                kind=ArtifactKind.MANIFEST,
                path=validator_summary_path,
                description="Normalized BIDS validator summary.",
                media_type="application/json",
                generated_by="bids_auditor",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=audit_report_path,
                description="Human-readable BIDS audit report.",
                media_type="text/markdown",
                generated_by="bids_auditor",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=triage_path,
                description="Actionable validator triage checklist.",
                media_type="text/markdown",
                generated_by="bids_auditor",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=stdout_path,
                description="Validator stdout log.",
                media_type="text/plain",
                generated_by="bids_auditor",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=stderr_path,
                description="Validator stderr log.",
                media_type="text/plain",
                generated_by="bids_auditor",
            ),
        ],
        provenance=ProvenanceRecord(
            commands=[command_record],
            software=[
                SoftwareInventoryRecord(name="clawneuro", version=__version__, role="orchestration"),
                SoftwareInventoryRecord(
                    name=config.validator_executable,
                    version=None,
                    role="validator",
                    container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
                ),
            ],
        ),
        handoff_targets=["deid_check", "mriqc_report", "anat_bold_prep", "diffusion_prep"],
        benchmark_tracks=["smoke"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=["BIDS validator normalization is deterministic given the captured JSON."],
    )
    return finalized_result
