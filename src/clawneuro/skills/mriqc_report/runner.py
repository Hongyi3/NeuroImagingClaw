"""Runner for the MRIQC report wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    CONTAINER_INPUT_ROOT,
    CONTAINER_OUTPUT_ROOT,
    CONTAINER_WORK_ROOT,
    CommandRecord,
    DatasetInventory,
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
    bidsapp_input_mount,
    bidsapp_output_mount,
    bidsapp_work_mount,
    collect_execution_provenance_evidence,
    detect_input_state,
    ensure_run_layout,
    execute_request,
    inspect_bids_dataset,
    planned_command_record,
    probe_command_version,
    resolve_executable,
)
from clawneuro.core.config import write_model_json
from clawneuro.core.models import ClawBaseModel, ProvenanceRecord
from clawneuro.reporting import (
    harvested_output_artifacts,
    harvest_mriqc_outputs,
)
from clawneuro.skills.common import finalize_skill_result
from clawneuro.skills.mriqc_report.config import MRIQCReportConfig

MRIQC_MODALITY_TO_CLI = {
    "anat": ["T1w", "T2w"],
    "bold": ["bold"],
}


def _format_mriqc_mem_gb(mem_gb: float) -> str:
    """Render MRIQC memory arguments using the integer-plus-unit grammar its parser expects."""

    if mem_gb.is_integer():
        return str(int(mem_gb))
    mem_mb = int(round(mem_gb * 1000))
    if mem_mb < 1:
        raise ValueError("MRIQC memory requests must be at least 1 MB.")
    return f"{mem_mb}M"


class MRIQCRunSummary(ClawBaseModel):
    """Machine-readable summary of planned or executed MRIQC behavior."""

    status: RunStatus
    derivative_root: Path
    participant_command: CommandRecord
    group_command: Optional[CommandRecord] = None
    modality_coverage: List[str] = Field(default_factory=list)
    report_paths: List[Path] = Field(default_factory=list)
    iqm_table_paths: List[Path] = Field(default_factory=list)
    dataset_description_path: Optional[Path] = None
    telemetry_disabled: bool = True
    failure_notes: List[str] = Field(default_factory=list)


def _normalize_requested_modalities(config: MRIQCReportConfig, inventory: DatasetInventory) -> List[str]:
    available = [item for item in inventory.modalities if item in {"anat", "bold"}]
    if not available:
        raise InvalidInputStateError(
            "mriqc_report requires anatomical and/or BOLD data in a BIDS dataset.",
            context={"path": str(config.bids_root), "modalities": inventory.modalities},
        )

    requested = config.modalities or available
    missing = sorted(set(requested) - set(available))
    if missing:
        raise InvalidInputStateError(
            "Requested MRIQC modalities are not present in the dataset.",
            context={"requested_modalities": requested, "available_modalities": available},
        )
    return requested


def _selected_participants(config: MRIQCReportConfig, inventory: DatasetInventory) -> List[str]:
    available = [subject.removeprefix("sub-") for subject in inventory.subject_ids]
    if not available:
        return []
    requested = config.participant_labels or available
    missing = sorted(set(requested) - set(available))
    if missing:
        raise InvalidInputStateError(
            "Requested participant labels are not present in the dataset.",
            context={"requested_participants": requested, "available_participants": available},
        )
    return requested


def _validate_requested_sessions(config: MRIQCReportConfig, inventory: DatasetInventory) -> None:
    if not config.session_ids:
        return
    available = [session.removeprefix("ses-") for session in inventory.session_ids]
    missing = sorted(set(config.session_ids) - set(available))
    if missing:
        raise InvalidInputStateError(
            "Requested session labels are not present in the dataset.",
            context={"requested_sessions": config.session_ids, "available_sessions": available},
        )


def _work_dir(config: MRIQCReportConfig, output_root: Path) -> Path:
    return config.work_dir or (output_root / "work")


def _mriqc_common_args(
    *,
    config: MRIQCReportConfig,
    bids_root: Path,
    derivative_root: Path,
    work_dir: Path,
    requested_modalities: List[str],
    analysis_level: str,
    participants: List[str],
) -> List[str]:
    args = [str(bids_root), str(derivative_root), analysis_level]
    if analysis_level == "participant" and participants:
        args.extend(["--participant-label", *participants])
    if config.session_ids:
        args.extend(["--session-id", *config.session_ids])
    if config.task_ids:
        args.extend(["--task-id", *config.task_ids])
    cli_modalities: List[str] = []
    for modality in requested_modalities:
        cli_modalities.extend(MRIQC_MODALITY_TO_CLI[modality])
    if cli_modalities:
        args.extend(["-m", *cli_modalities])
    if config.nprocs is not None:
        args.extend(["--nprocs", str(config.nprocs)])
    if config.omp_nthreads is not None:
        args.extend(["--omp-nthreads", str(config.omp_nthreads)])
    if config.mem_gb is not None:
        args.extend(["--mem_gb", _format_mriqc_mem_gb(config.mem_gb)])
    args.extend(["-w", str(work_dir)])
    if config.no_sub:
        args.append("--no-sub")
    return args


def build_mriqc_participant_request(
    config: MRIQCReportConfig,
    inventory: DatasetInventory,
    derivative_root: Path,
) -> ExecutionRequest:
    """Build the participant-level MRIQC request."""

    requested_modalities = _normalize_requested_modalities(config, inventory)
    participants = _selected_participants(config, inventory)
    work_dir = _work_dir(config, config.output_root)
    bids_root = config.bids_root
    output_root = derivative_root
    work_root = work_dir
    bind_mounts = []

    if config.backend != ExecutionBackend.LOCAL_BINARY:
        bind_mounts = [
            bidsapp_input_mount(config.bids_root),
            bidsapp_output_mount(derivative_root),
            bidsapp_work_mount(work_dir),
        ]
        bids_root = CONTAINER_INPUT_ROOT
        output_root = CONTAINER_OUTPUT_ROOT
        work_root = CONTAINER_WORK_ROOT

    return ExecutionRequest(
        name="mriqc-participant",
        backend=config.backend,
        executable=config.mriqc_executable,
        args=_mriqc_common_args(
            config=config,
            bids_root=bids_root,
            derivative_root=output_root,
            work_dir=work_root,
            requested_modalities=requested_modalities,
            analysis_level="participant",
            participants=participants,
        ),
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        bind_mounts=bind_mounts,
        description="Run MRIQC at participant level with explicit modality and participant filters.",
        use_container_entrypoint=config.backend != ExecutionBackend.LOCAL_BINARY,
    )


def build_mriqc_group_request(
    config: MRIQCReportConfig,
    inventory: DatasetInventory,
    derivative_root: Path,
) -> ExecutionRequest:
    """Build the optional group-level MRIQC request."""

    requested_modalities = _normalize_requested_modalities(config, inventory)
    work_dir = _work_dir(config, config.output_root)
    bids_root = config.bids_root
    output_root = derivative_root
    work_root = work_dir
    bind_mounts = []

    if config.backend != ExecutionBackend.LOCAL_BINARY:
        bind_mounts = [
            bidsapp_input_mount(config.bids_root),
            bidsapp_output_mount(derivative_root),
            bidsapp_work_mount(work_dir),
        ]
        bids_root = CONTAINER_INPUT_ROOT
        output_root = CONTAINER_OUTPUT_ROOT
        work_root = CONTAINER_WORK_ROOT

    return ExecutionRequest(
        name="mriqc-group",
        backend=config.backend,
        executable=config.mriqc_executable,
        args=_mriqc_common_args(
            config=config,
            bids_root=bids_root,
            derivative_root=output_root,
            work_dir=work_root,
            requested_modalities=requested_modalities,
            analysis_level="group",
            participants=[],
        ),
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        bind_mounts=bind_mounts,
        description="Run MRIQC at group level after participant-level QC has completed.",
        use_container_entrypoint=config.backend != ExecutionBackend.LOCAL_BINARY,
    )


def _tool_software_inventory(config: MRIQCReportConfig, request: ExecutionRequest) -> SoftwareInventoryRecord:
    version = None
    source = None
    notes_source = request.environment if request.environment else None
    if config.backend == ExecutionBackend.LOCAL_BINARY:
        version = probe_command_version(config.mriqc_executable, environment=notes_source)
        resolved = resolve_executable(config.mriqc_executable, environment=notes_source)
        source = str(resolved) if resolved is not None else None
    return SoftwareInventoryRecord(
        name="mriqc",
        version=version,
        role="qc",
        source=source,
        container_image=config.container_image,
    )


def _summary_markdown(summary: MRIQCRunSummary) -> str:
    lines = [
        "# MRIQC Report Wrapper Summary",
        "",
        f"- Status: `{summary.status.value}`",
        f"- Derivative root: `{summary.derivative_root}`",
        f"- Modalities: {', '.join(summary.modality_coverage) if summary.modality_coverage else 'none'}",
        f"- Telemetry disabled: `{str(summary.telemetry_disabled).lower()}`",
        f"- HTML reports: {len(summary.report_paths)}",
        f"- IQM tables: {len(summary.iqm_table_paths)}",
        "",
        "## Commands",
        f"- participant: `{summary.participant_command.shell_command}`",
    ]
    if summary.group_command is not None:
        lines.append(f"- group: `{summary.group_command.shell_command}`")
    lines.extend(["", "## Failure Notes"])
    if summary.failure_notes:
        lines.extend(f"- {note}" for note in summary.failure_notes)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def run_mriqc_report(config: MRIQCReportConfig) -> SkillResult:
    """Plan or run MRIQC and preserve report and IQM artifact locations."""

    input_state = detect_input_state(config.bids_root)
    if input_state.kind not in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        raise InvalidInputStateError(
            "mriqc_report requires a BIDS dataset root.",
            context={"path": str(config.bids_root), "detected_kind": input_state.kind.value},
        )

    inventory = inspect_bids_dataset(config.bids_root)
    requested_modalities = _normalize_requested_modalities(config, inventory)
    _validate_requested_sessions(config, inventory)
    layout = ensure_run_layout(config.output_root)
    _work_dir(config, config.output_root).mkdir(parents=True, exist_ok=True)
    derivative_root = layout.derivatives_dir
    participant_request = build_mriqc_participant_request(config, inventory, derivative_root)
    group_request = build_mriqc_group_request(config, inventory, derivative_root) if config.run_group else None

    participant_stdout = layout.logs_dir / "mriqc-participant.stdout.log"
    participant_stderr = layout.logs_dir / "mriqc-participant.stderr.log"
    group_stdout = layout.logs_dir / "mriqc-group.stdout.log"
    group_stderr = layout.logs_dir / "mriqc-group.stderr.log"

    warnings: List[WarningRecord] = []
    failure_notes: List[str] = []
    runtime_notes: List[str] = []
    runtime_evidence = None

    if not config.no_sub:
        warnings.append(
            WarningRecord(
                code="mriqc-telemetry-enabled",
                severity=WarningSeverity.WARNING,
                message="MRIQC telemetry upload suppression is disabled for this request.",
                hint="Set no_sub=true to keep the default local-only privacy posture.",
            )
        )

    if config.execute:
        participant_command = execute_request(
            participant_request,
            stdout_path=participant_stdout,
            stderr_path=participant_stderr,
        )
        if participant_command.status == RunStatus.FAILED:
            status = RunStatus.FAILED
            group_command = (
                planned_command_record(group_request).model_copy(update={"status": RunStatus.SKIPPED})
                if group_request is not None
                else None
            )
        else:
            if group_request is not None:
                group_command = execute_request(
                    group_request,
                    stdout_path=group_stdout,
                    stderr_path=group_stderr,
                )
            else:
                group_command = None
            if group_command is not None and group_command.status == RunStatus.FAILED:
                status = RunStatus.FAILED
            else:
                harvest = harvest_mriqc_outputs(derivative_root)
                if not harvest.report_paths:
                    failure_notes.append(
                        "MRIQC execution completed but no upstream HTML reports were harvested from the derivative root."
                    )
                if not harvest.iqm_table_paths:
                    failure_notes.append(
                        "MRIQC execution completed but no IQM tables were harvested from the derivative root."
                    )
                if harvest.dataset_description_path is None:
                    failure_notes.append(
                        "MRIQC execution completed but no derivative dataset_description.json was harvested."
                    )
                if participant_request.backend != ExecutionBackend.LOCAL_BINARY:
                    runtime_evidence = collect_execution_provenance_evidence(
                        participant_request,
                        tool_name="mriqc",
                        tool_role="qc",
                    )
                    runtime_notes = runtime_evidence.notes
                    if not runtime_evidence.complete:
                        failure_notes.extend(runtime_notes)
                status = RunStatus.SUCCEEDED if not failure_notes else RunStatus.PARTIAL
    else:
        participant_command = planned_command_record(participant_request)
        group_command = planned_command_record(group_request) if group_request is not None else None
        status = RunStatus.PLANNED

    harvest = harvest_mriqc_outputs(derivative_root)
    if status == RunStatus.PARTIAL:
        warnings.append(
            WarningRecord(
                code="mriqc-artifacts-incomplete",
                severity=WarningSeverity.WARNING,
                message="MRIQC execution completed with incomplete preserved outputs.",
                hint="Inspect harvested reports, IQM tables, and derivative metadata before treating the run as complete.",
            )
        )
    if status == RunStatus.FAILED:
        warnings.append(
            WarningRecord(
                code="mriqc-execution-failed",
                severity=WarningSeverity.ERROR,
                message="MRIQC execution failed before the expected QC artifacts were harvested.",
                hint="Inspect the participant/group stdout and stderr logs.",
            )
        )

    summary = MRIQCRunSummary(
        status=status,
        derivative_root=derivative_root,
        participant_command=participant_command,
        group_command=group_command,
        modality_coverage=requested_modalities,
        report_paths=harvest.report_paths,
        iqm_table_paths=harvest.iqm_table_paths,
        dataset_description_path=harvest.dataset_description_path,
        telemetry_disabled=config.no_sub,
        failure_notes=failure_notes,
    )
    summary_path = write_model_json(layout.manifests_dir / "mriqc-summary.json", summary)
    report_path = layout.report_dir / "mriqc-report.md"
    report_path.write_text(_summary_markdown(summary), encoding="utf-8")

    result = SkillResult(
        skill=SkillDescriptor(
            name="mriqc_report",
            kind=SkillKind.QC,
            version=__version__,
            contract_path=Path("skills/mriqc_report/SKILL.md"),
        ),
        status=status,
        summary=(
            "Planned MRIQC participant and optional group execution with preserved QC artifact locations."
            if status == RunStatus.PLANNED
            else "MRIQC completed and preserved HTML reports, IQM tables, and derivative metadata."
            if status == RunStatus.SUCCEEDED
            else "MRIQC completed but preserved outputs were incomplete; inspect the summary and logs before treating the run as complete."
            if status == RunStatus.PARTIAL
            else "MRIQC execution failed; inspect the captured command logs."
        ),
        input_state=input_state,
        dataset_inventory=inventory,
        warnings=warnings,
        artifacts=[
            ArtifactRecord(
                kind=ArtifactKind.MANIFEST,
                path=summary_path,
                description="Machine-readable MRIQC wrapper summary.",
                media_type="application/json",
                generated_by="mriqc_report",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=report_path,
                description="Human-readable MRIQC wrapper summary.",
                media_type="text/markdown",
                generated_by="mriqc_report",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=participant_stdout,
                description="MRIQC participant stdout log.",
                media_type="text/plain",
                generated_by="mriqc_report",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=participant_stderr,
                description="MRIQC participant stderr log.",
                media_type="text/plain",
                generated_by="mriqc_report",
            ),
            *(
                [
                    ArtifactRecord(
                        kind=ArtifactKind.LOG,
                        path=group_stdout,
                        description="MRIQC group stdout log.",
                        media_type="text/plain",
                        generated_by="mriqc_report",
                    ),
                    ArtifactRecord(
                        kind=ArtifactKind.LOG,
                        path=group_stderr,
                        description="MRIQC group stderr log.",
                        media_type="text/plain",
                        generated_by="mriqc_report",
                    ),
                ]
                if group_request is not None
                else []
            ),
            *harvested_output_artifacts(harvest, generated_by="mriqc_report"),
        ],
        provenance=ProvenanceRecord(
            commands=[command for command in [participant_command, group_command] if command is not None],
            software=(
                [SoftwareInventoryRecord(name="clawneuro", version=__version__, role="orchestration")]
                + (
                    runtime_evidence.software
                    if runtime_evidence is not None
                    else [_tool_software_inventory(config, participant_request)]
                )
            ),
            notes=[
                "MRIQC participant and optional group runs are recorded as separate commands to keep artifact provenance explicit.",
                *runtime_notes,
            ],
        ),
        handoff_targets=["anat_bold_prep", "report_bundle"],
        benchmark_tracks=["smoke", "task-fmri", "resting-state"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=[
            "MRIQC requests keep participant and optional group runs explicit rather than depending on implicit upstream behavior.",
        ],
    )
    return finalized_result
