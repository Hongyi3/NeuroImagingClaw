"""Runner for the BIDS auditor skill."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    BindMount,
    CommandRecord,
    CONTAINER_CONFIG_ROOT,
    CONTAINER_INPUT_ROOT,
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


class ValidatorEvidenceMode(str, Enum):
    """Source mode for validator summaries."""

    PLANNED = "planned"
    LIVE_EXECUTION = "live_execution"
    PINNED_FIDELITY_FIXTURE = "pinned_fidelity_fixture"


class ValidatorEvidence(ClawBaseModel):
    """Evidence metadata attached to a validator summary."""

    mode: ValidatorEvidenceMode
    tool_name: str
    tool_version: Optional[str] = None
    output_format: str = "json"
    source_dataset: Optional[str] = None
    source_reference: Optional[str] = None
    fixture_path: Optional[Path] = None
    notes: List[str] = Field(default_factory=list)


class ValidatorSummary(ClawBaseModel):
    """Machine-readable validator summary."""

    status: RunStatus
    errors: int = 0
    warnings: int = 0
    issues: List[ValidatorIssue] = Field(default_factory=list)
    schema_version: Optional[str] = None
    evidence: ValidatorEvidence = Field(
        default_factory=lambda: ValidatorEvidence(
            mode=ValidatorEvidenceMode.PLANNED,
            tool_name="bids-validator",
        )
    )


def _issue_category(issue: Mapping[str, Any]) -> str:
    code = str(issue.get("code", "")).lower()
    message = str(
        issue.get("reason", "")
        or issue.get("message", "")
        or issue.get("issueMessage", "")
        or issue.get("subCode", "")
    ).lower()
    if "json" in code or "metadata" in code or "metadata" in message:
        return "metadata"
    if "subject" in code or "structure" in code or "folder" in message:
        return "structure"
    return "general"


def normalize_validator_output(
    raw: Mapping[str, Any],
    status: RunStatus,
    evidence: Optional[ValidatorEvidence] = None,
) -> ValidatorSummary:
    """Normalize common BIDS validator JSON shapes."""

    issues_section = raw.get("issues", {})
    normalized_issues: List[ValidatorIssue] = []
    error_count = 0
    warning_count = 0

    if isinstance(issues_section, Mapping) and isinstance(issues_section.get("errors"), list):
        errors = issues_section.get("errors", [])
        warnings = issues_section.get("warnings", [])
        for raw_issue in list(errors) + list(warnings):
            if not isinstance(raw_issue, Mapping):
                continue
            severity = WarningSeverity.ERROR if raw_issue in errors else WarningSeverity.WARNING
            if severity == WarningSeverity.ERROR:
                error_count += 1
            else:
                warning_count += 1
            normalized_issues.append(
                ValidatorIssue(
                    code=str(raw_issue.get("code", "validator-issue")),
                    severity=severity,
                    category=_issue_category(raw_issue),
                    message=str(
                        raw_issue.get("reason", "")
                        or raw_issue.get("message", "")
                        or raw_issue.get("issueMessage", "")
                        or raw_issue.get("subCode", "")
                        or "Validator issue"
                    ),
                    location=str(raw_issue.get("location")) if raw_issue.get("location") else None,
                )
            )
    elif isinstance(issues_section, Mapping) and isinstance(issues_section.get("issues"), list):
        for raw_issue in issues_section.get("issues", []):
            if not isinstance(raw_issue, Mapping):
                continue
            severity_name = str(raw_issue.get("severity", "warning")).lower()
            severity = WarningSeverity.ERROR if severity_name == "error" else WarningSeverity.WARNING
            if severity == WarningSeverity.ERROR:
                error_count += 1
            else:
                warning_count += 1
            affects = raw_issue.get("affects")
            location = raw_issue.get("location")
            if location is None and isinstance(affects, list) and affects:
                location = affects[0]
            normalized_issues.append(
                ValidatorIssue(
                    code=str(raw_issue.get("code", "validator-issue")),
                    severity=severity,
                    category=_issue_category(raw_issue),
                    message=str(
                        raw_issue.get("reason", "")
                        or raw_issue.get("message", "")
                        or raw_issue.get("issueMessage", "")
                        or raw_issue.get("subCode", "")
                        or raw_issue.get("code", "Validator issue")
                    ),
                    location=str(location) if location else None,
                )
            )

    schema_version = None
    summary = raw.get("summary")
    if isinstance(summary, Mapping):
        schema_version = str(summary.get("schemaVersion")) if summary.get("schemaVersion") else None

    return ValidatorSummary(
        status=status,
        errors=error_count,
        warnings=warning_count,
        issues=normalized_issues,
        schema_version=schema_version,
        evidence=evidence
        or ValidatorEvidence(
            mode=ValidatorEvidenceMode.PLANNED,
            tool_name="bids-validator",
        ),
    )


def build_validator_request(config: BidsAuditorConfig) -> ExecutionRequest:
    """Create the validator execution request for the chosen backend."""

    bids_root = config.bids_root
    validator_config = config.validator_config
    bind_mounts: List[BindMount] = []

    if config.backend != ExecutionBackend.LOCAL_BINARY:
        bind_mounts.append(
            BindMount(source=config.bids_root, target=CONTAINER_INPUT_ROOT, read_only=True)
        )
        bids_root = CONTAINER_INPUT_ROOT
        if validator_config is not None:
            bind_mounts.append(
                BindMount(
                    source=validator_config.parent,
                    target=CONTAINER_CONFIG_ROOT,
                    read_only=True,
                )
            )
            validator_config = CONTAINER_CONFIG_ROOT / validator_config.name

    args = [str(bids_root), "--format", config.validator_format]
    if validator_config is not None:
        args.extend(["--config", str(validator_config)])
    if config.participant_labels:
        args.extend(["--participant-label"] + config.participant_labels)
    return ExecutionRequest(
        name="bids-validator",
        backend=config.backend,
        executable=config.validator_executable,
        args=args,
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        bind_mounts=bind_mounts,
        description="Validate a BIDS dataset and emit machine-readable JSON.",
        use_container_entrypoint=config.backend != ExecutionBackend.LOCAL_BINARY,
    )


def _render_audit_report(summary: ValidatorSummary, inventory_name: str) -> ReportBundleDraft:
    body = "\n".join(
        [
            "Validator status: `{0}`".format(summary.status.value),
            "Errors: {0}".format(summary.errors),
            "Warnings: {0}".format(summary.warnings),
            "Evidence mode: `{0}`".format(summary.evidence.mode.value),
        ]
    )
    if summary.schema_version:
        body = body + "\nSchema version: `{0}`".format(summary.schema_version)
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
        evidence = ValidatorEvidence(
            mode=ValidatorEvidenceMode.LIVE_EXECUTION,
            tool_name=config.validator_executable,
            output_format=config.validator_format,
            notes=[
                "Validator output was captured from an executed command in this run.",
            ],
        )
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
        evidence = ValidatorEvidence(
            mode=ValidatorEvidenceMode.PLANNED,
            tool_name=config.validator_executable,
            output_format=config.validator_format,
            notes=["Validator command was planned but not executed in this run."],
        )
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

    summary = normalize_validator_output(raw_validator_output, status=status, evidence=evidence)
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
            if status == RunStatus.PLANNED
            else "Validator execution failed; inspect the captured logs and normalized summary."
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
