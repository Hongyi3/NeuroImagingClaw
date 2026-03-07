"""Runner for the anat + BOLD preprocessing wrapper."""

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
    bidsapp_license_file_mount,
    bidsapp_output_mount,
    bidsapp_upstream_derivative_mount,
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
    harvest_fmriprep_outputs,
)
from clawneuro.skills.anat_bold_prep.config import AnatBoldPrepConfig
from clawneuro.skills.common import finalize_skill_result


class AnatBoldPrepSummary(ClawBaseModel):
    """Machine-readable summary of planned or executed preprocessing."""

    status: RunStatus
    derivative_root: Path
    command: CommandRecord
    report_paths: List[Path] = Field(default_factory=list)
    dataset_description_path: Optional[Path] = None
    boilerplate_paths: List[Path] = Field(default_factory=list)
    confounds_paths: List[Path] = Field(default_factory=list)
    output_spaces: List[str] = Field(default_factory=list)
    confounds_file_count: int = 0
    freesurfer_enabled: bool = False
    reuse_derivative_roots: List[Path] = Field(default_factory=list)
    failure_notes: List[str] = Field(default_factory=list)


def _selected_participants(config: AnatBoldPrepConfig, inventory: DatasetInventory) -> List[str]:
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


def _validate_input_modalities(config: AnatBoldPrepConfig, inventory: DatasetInventory) -> None:
    if "anat" not in inventory.modalities:
        raise InvalidInputStateError(
            "anat_bold_prep requires anatomical input.",
            context={"path": str(config.bids_root), "modalities": inventory.modalities},
        )
    if not config.anat_only and "bold" not in inventory.modalities:
        raise InvalidInputStateError(
            "anat_bold_prep requires BOLD input unless anat_only is true.",
            context={"path": str(config.bids_root), "modalities": inventory.modalities},
        )


def _work_dir(config: AnatBoldPrepConfig, output_root: Path) -> Path:
    return config.work_dir or (output_root / "work")


def build_anat_bold_prep_request(
    config: AnatBoldPrepConfig,
    inventory: DatasetInventory,
    derivative_root: Path,
) -> ExecutionRequest:
    """Build the fMRIPrep command request."""

    _validate_input_modalities(config, inventory)
    participants = _selected_participants(config, inventory)
    work_dir = _work_dir(config, config.output_root)
    bids_root = config.bids_root
    output_root = derivative_root
    work_root = work_dir
    license_path = config.fs_license_file
    bind_mounts = []
    derivatives_args = [str(path) for path in config.reuse_derivative_roots]

    if config.backend != ExecutionBackend.LOCAL_BINARY:
        bind_mounts = [
            bidsapp_input_mount(config.bids_root),
            bidsapp_output_mount(derivative_root),
            bidsapp_work_mount(work_dir),
        ]
        bids_root = CONTAINER_INPUT_ROOT
        output_root = CONTAINER_OUTPUT_ROOT
        work_root = CONTAINER_WORK_ROOT
        if config.freesurfer_enabled and config.fs_license_file is not None:
            license_mount, license_path = bidsapp_license_file_mount(config.fs_license_file)
            bind_mounts.append(license_mount)
        derivatives_args = []
        for index, derivative_root_path in enumerate(config.reuse_derivative_roots, start=1):
            derivative_mount, mounted_path = bidsapp_upstream_derivative_mount(
                derivative_root_path,
                label=f"reuse-{index}",
            )
            bind_mounts.append(derivative_mount)
            derivatives_args.append(str(mounted_path))

    args = [str(bids_root), str(output_root), "participant"]
    if participants:
        args.extend(["--participant-label", *participants])
    if config.anat_only:
        args.append("--anat-only")
    args.extend(["--output-layout", config.output_layout])
    if config.output_spaces:
        args.extend(["--output-spaces", *config.output_spaces])
    args.extend(["--work-dir", str(work_root)])
    if config.notrack:
        args.append("--notrack")
    if config.freesurfer_enabled and license_path is not None:
        args.extend(["--fs-license-file", str(license_path)])
    else:
        args.append("--fs-no-reconall")
    if derivatives_args:
        args.extend(["--derivatives", *derivatives_args])
    if config.nprocs is not None:
        args.extend(["--nprocs", str(config.nprocs)])
    if config.omp_nthreads is not None:
        args.extend(["--omp-nthreads", str(config.omp_nthreads)])
    if config.mem_mb is not None:
        args.extend(["--mem-mb", str(config.mem_mb)])

    return ExecutionRequest(
        name="anat-bold-prep",
        backend=config.backend,
        executable=config.fmriprep_executable,
        args=args,
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        bind_mounts=bind_mounts,
        description="Run BIDS-layout structural and BOLD preprocessing with explicit boilerplate capture points.",
        use_container_entrypoint=config.backend != ExecutionBackend.LOCAL_BINARY,
    )


def _tool_software_inventory(config: AnatBoldPrepConfig, request: ExecutionRequest) -> SoftwareInventoryRecord:
    version = None
    source = None
    if config.backend == ExecutionBackend.LOCAL_BINARY:
        version = probe_command_version(config.fmriprep_executable, environment=request.environment)
        resolved = resolve_executable(config.fmriprep_executable, environment=request.environment)
        source = str(resolved) if resolved is not None else None
    return SoftwareInventoryRecord(
        name="fmriprep",
        version=version,
        role="preprocessing",
        source=source,
        container_image=config.container_image,
    )


def _summary_markdown(summary: AnatBoldPrepSummary) -> str:
    lines = [
        "# Anatomical and BOLD Preprocessing Summary",
        "",
        f"- Status: `{summary.status.value}`",
        f"- Derivative root: `{summary.derivative_root}`",
        f"- Output spaces: {', '.join(summary.output_spaces) if summary.output_spaces else 'default upstream spaces'}",
        f"- FreeSurfer enabled: `{str(summary.freesurfer_enabled).lower()}`",
        f"- Preserved HTML reports: {len(summary.report_paths)}",
        f"- Preserved boilerplate files: {len(summary.boilerplate_paths)}",
        f"- Preserved confounds files: {summary.confounds_file_count}",
        "",
        "## Command",
        f"`{summary.command.shell_command}`",
        "",
        "## Failure Notes",
    ]
    if summary.failure_notes:
        lines.extend(f"- {note}" for note in summary.failure_notes)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def run_anat_bold_prep(config: AnatBoldPrepConfig) -> SkillResult:
    """Plan or run anat + BOLD preprocessing and preserve upstream artifacts."""

    input_state = detect_input_state(config.bids_root)
    if input_state.kind not in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        raise InvalidInputStateError(
            "anat_bold_prep requires a BIDS dataset root.",
            context={"path": str(config.bids_root), "detected_kind": input_state.kind.value},
        )

    inventory = inspect_bids_dataset(config.bids_root)
    _validate_input_modalities(config, inventory)
    layout = ensure_run_layout(config.output_root)
    _work_dir(config, config.output_root).mkdir(parents=True, exist_ok=True)
    derivative_root = layout.derivatives_dir
    request = build_anat_bold_prep_request(config, inventory, derivative_root)
    stdout_path = layout.logs_dir / "anat-bold-prep.stdout.log"
    stderr_path = layout.logs_dir / "anat-bold-prep.stderr.log"

    warnings: List[WarningRecord] = []
    failure_notes: List[str] = []
    runtime_notes: List[str] = []
    runtime_evidence = None

    if not config.notrack:
        warnings.append(
            WarningRecord(
                code="fmriprep-tracking-enabled",
                severity=WarningSeverity.WARNING,
                message="fMRIPrep tracking suppression is disabled for this request.",
                hint="Set notrack=true to keep the default local-only privacy posture.",
            )
        )

    if config.execute:
        command = execute_request(request, stdout_path=stdout_path, stderr_path=stderr_path)
        if command.status == RunStatus.FAILED:
            status = RunStatus.FAILED
        else:
            harvest = harvest_fmriprep_outputs(derivative_root)
            if not harvest.report_paths:
                failure_notes.append(
                    "Preprocessing completed but no preserved HTML reports were harvested from the derivative root."
                )
            if not harvest.boilerplate_paths:
                failure_notes.append(
                    "Preprocessing completed but no boilerplate/citation files were harvested from logs/."
                )
            if harvest.dataset_description_path is None:
                failure_notes.append(
                    "Preprocessing completed but no derivative dataset_description.json was harvested."
                )
            if request.backend != ExecutionBackend.LOCAL_BINARY:
                runtime_evidence = collect_execution_provenance_evidence(
                    request,
                    tool_name="fmriprep",
                    tool_role="preprocessing",
                )
                runtime_notes = runtime_evidence.notes
                if not runtime_evidence.complete:
                    failure_notes.extend(runtime_notes)
            status = RunStatus.SUCCEEDED if not failure_notes else RunStatus.PARTIAL
    else:
        command = planned_command_record(request)
        status = RunStatus.PLANNED

    harvest = harvest_fmriprep_outputs(derivative_root)
    if status == RunStatus.PARTIAL:
        warnings.append(
            WarningRecord(
                code="anat-bold-prep-artifacts-incomplete",
                severity=WarningSeverity.WARNING,
                message="Preprocessing execution completed with incomplete preserved outputs.",
                hint="Inspect harvested reports, boilerplate files, and derivative metadata before treating the run as complete.",
            )
        )
    if status == RunStatus.FAILED:
        warnings.append(
            WarningRecord(
                code="anat-bold-prep-execution-failed",
                severity=WarningSeverity.ERROR,
                message="Preprocessing execution failed before the expected outputs were harvested.",
                hint="Inspect the captured stdout and stderr logs.",
            )
        )

    summary = AnatBoldPrepSummary(
        status=status,
        derivative_root=derivative_root,
        command=command,
        report_paths=harvest.report_paths,
        dataset_description_path=harvest.dataset_description_path,
        boilerplate_paths=harvest.boilerplate_paths,
        confounds_paths=harvest.confounds_paths,
        output_spaces=config.output_spaces,
        confounds_file_count=len(harvest.confounds_paths),
        freesurfer_enabled=config.freesurfer_enabled,
        reuse_derivative_roots=config.reuse_derivative_roots,
        failure_notes=failure_notes,
    )
    summary_path = write_model_json(layout.manifests_dir / "anat-bold-prep-summary.json", summary)
    report_path = layout.report_dir / "anat-bold-prep-report.md"
    report_path.write_text(_summary_markdown(summary), encoding="utf-8")

    result = SkillResult(
        skill=SkillDescriptor(
            name="anat_bold_prep",
            kind=SkillKind.PREPROCESSING,
            version=__version__,
            contract_path=Path("skills/anat_bold_prep/SKILL.md"),
        ),
        status=status,
        summary=(
            "Planned anat + BOLD preprocessing with explicit report, boilerplate, and derivative metadata capture."
            if status == RunStatus.PLANNED
            else "Preprocessing completed and preserved reports, boilerplate, and derivative metadata."
            if status == RunStatus.SUCCEEDED
            else "Preprocessing completed but preserved outputs were incomplete; inspect the summary and logs before treating the run as complete."
            if status == RunStatus.PARTIAL
            else "Preprocessing execution failed; inspect the captured logs."
        ),
        input_state=input_state,
        dataset_inventory=inventory,
        warnings=warnings,
        artifacts=[
            ArtifactRecord(
                kind=ArtifactKind.MANIFEST,
                path=summary_path,
                description="Machine-readable preprocessing wrapper summary.",
                media_type="application/json",
                generated_by="anat_bold_prep",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=report_path,
                description="Human-readable preprocessing wrapper summary.",
                media_type="text/markdown",
                generated_by="anat_bold_prep",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=stdout_path,
                description="Preprocessing stdout log.",
                media_type="text/plain",
                generated_by="anat_bold_prep",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=stderr_path,
                description="Preprocessing stderr log.",
                media_type="text/plain",
                generated_by="anat_bold_prep",
            ),
            *harvested_output_artifacts(harvest, generated_by="anat_bold_prep"),
        ],
        provenance=ProvenanceRecord(
            commands=[command],
            software=(
                [SoftwareInventoryRecord(name="clawneuro", version=__version__, role="orchestration")]
                + (
                    runtime_evidence.software
                    if runtime_evidence is not None
                    else [_tool_software_inventory(config, request)]
                )
            ),
            notes=[
                "Preprocessing requests keep report, boilerplate, and derivative metadata harvest points explicit in the run manifest.",
                *runtime_notes,
            ],
        ),
        handoff_targets=["task_glm", "rest_connectivity", "report_bundle", "repro_bundle"],
        benchmark_tracks=["smoke", "task-fmri", "resting-state"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=[
            "fMRIPrep-family requests are rendered with --output-layout bids, explicit work-dir handling, and preserved boilerplate capture points.",
        ],
    )
    return finalized_result
