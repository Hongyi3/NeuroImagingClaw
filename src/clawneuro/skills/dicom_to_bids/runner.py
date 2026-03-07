"""Runner for the DICOM-to-BIDS skill."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    BindMount,
    CommandRecord,
    CONTAINER_CONFIG_ROOT,
    CONTAINER_INPUT_ROOT,
    CONTAINER_OUTPUT_ROOT,
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
    detect_input_state,
    ensure_run_layout,
    execute_request,
    inspect_bids_dataset,
    planned_command_record,
    prepend_executable_parent_to_path,
    probe_command_version,
    resolve_executable,
)
from clawneuro.core.config import write_model_json
from clawneuro.core.models import ClawBaseModel, ProvenanceRecord
from clawneuro.reporting import render_markdown_report
from clawneuro.reporting.models import ReportBundleDraft, ReportSection
from clawneuro.skills.bids_auditor.config import BidsAuditorConfig
from clawneuro.skills.bids_auditor.runner import build_validator_request
from clawneuro.skills.common import finalize_skill_result
from clawneuro.skills.dicom_to_bids.config import CurationBackend, DicomToBidsConfig

VERSION_PROBE_ARGS: Dict[str, List[List[str]]] = {
    "dcm2bids": [["--version"]],
    "heudiconv": [["--version"]],
    "dcm2niix": [["--version"], ["-v"]],
    "bids-validator-deno": [["--version"]],
}


class ExecutionStepRecord(ClawBaseModel):
    """Structured record for one wrapped execution step."""

    name: str
    description: str
    command: CommandRecord
    log_paths: List[Path] = Field(default_factory=list)
    artifact_paths: List[Path] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class ToolRuntimeEvidence(ClawBaseModel):
    """Resolved runtime details for one required tool."""

    tool_name: str
    requested_executable: str
    resolved_executable: Optional[Path] = None
    version: Optional[str] = None
    available: bool = False
    version_captured: bool = False
    container_image: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class ConversionRuntimeEvidence(ClawBaseModel):
    """Runtime proof recorded alongside the conversion manifest."""

    backend: ExecutionBackend
    tools: List[ToolRuntimeEvidence] = Field(default_factory=list)
    required_runtimes_resolved: bool = False
    versions_captured: bool = False
    runtime_provenance_complete: bool = False
    notes: List[str] = Field(default_factory=list)


class ConversionManifest(ClawBaseModel):
    """Machine-readable summary of the planned or executed conversion workflow."""

    status: RunStatus
    bids_root: Path
    curation_backend: CurationBackend
    participant_label: str
    session_label: str | None = None
    conversion_step: ExecutionStepRecord
    validator_step: ExecutionStepRecord
    runtime_evidence: ConversionRuntimeEvidence
    unresolved_metadata: List[str] = Field(default_factory=list)


def _curation_executable(config: DicomToBidsConfig) -> str:
    if config.curation_executable:
        return config.curation_executable
    return "dcm2bids" if config.curation_backend == CurationBackend.DCM2BIDS else "heudiconv"


def _curation_tool_name(config: DicomToBidsConfig) -> str:
    return "dcm2bids" if config.curation_backend == CurationBackend.DCM2BIDS else "heudiconv"


def _validator_tool_name(_: DicomToBidsConfig) -> str:
    return "bids-validator-deno"


def _local_curation_environment(config: DicomToBidsConfig) -> Dict[str, str]:
    if config.backend != ExecutionBackend.LOCAL_BINARY:
        return {}
    return prepend_executable_parent_to_path(config.dcm2niix_executable)


def _runtime_notes(config: DicomToBidsConfig) -> List[str]:
    notes: List[str] = []
    if os.path.sep in config.dcm2niix_executable or (os.path.altsep and os.path.altsep in config.dcm2niix_executable):
        notes.append(
            "Local execution PATH was augmented with the configured dcm2niix parent directory."
        )
    return notes


def _probe_local_tool(tool_name: str, executable: str, environment: Optional[Dict[str, str]] = None) -> ToolRuntimeEvidence:
    resolved = resolve_executable(executable, environment=environment)
    version = probe_command_version(
        executable,
        environment=environment,
        version_args=VERSION_PROBE_ARGS.get(tool_name, [["--version"]]),
    )
    notes: List[str] = []
    if resolved is None:
        notes.append("Executable could not be resolved on the effective PATH.")
    if resolved is not None and version is None:
        notes.append("Executable resolved, but version probing did not return a stable string.")
    return ToolRuntimeEvidence(
        tool_name=tool_name,
        requested_executable=executable,
        resolved_executable=resolved,
        version=version,
        available=resolved is not None,
        version_captured=version is not None,
        notes=notes,
    )


def build_runtime_evidence(
    config: DicomToBidsConfig,
    curation_request: ExecutionRequest,
    validator_request: ExecutionRequest,
) -> ConversionRuntimeEvidence:
    """Capture runtime proof for the selected execution backend."""

    notes = _runtime_notes(config)
    if config.backend != ExecutionBackend.LOCAL_BINARY:
        tools = [
            ToolRuntimeEvidence(
                tool_name=_curation_tool_name(config),
                requested_executable=_curation_executable(config),
                available=bool(config.conversion_image),
                container_image=config.conversion_image,
                notes=["Wrapped tool will run through a pinned container image."],
            ),
            ToolRuntimeEvidence(
                tool_name="dcm2niix",
                requested_executable=config.dcm2niix_executable,
                available=bool(config.conversion_image),
                container_image=config.conversion_image,
                notes=["dcm2niix is expected to be provided by the selected conversion image."],
            ),
            ToolRuntimeEvidence(
                tool_name=_validator_tool_name(config),
                requested_executable=config.validator_executable,
                available=bool(config.validator_image),
                container_image=config.validator_image,
                notes=["Validator will run through a pinned container image."],
            ),
        ]
        return ConversionRuntimeEvidence(
            backend=config.backend,
            tools=tools,
            required_runtimes_resolved=all(tool.available for tool in tools),
            versions_captured=False,
            runtime_provenance_complete=False,
            notes=notes
            + [
                "Container execution keeps image references explicit, but this repository records tool versions from local execution for M3 evidence.",
            ],
        )

    tools = [
        _probe_local_tool(
            _curation_tool_name(config),
            curation_request.executable,
            environment=curation_request.environment,
        ),
        _probe_local_tool(
            "dcm2niix",
            config.dcm2niix_executable,
            environment=curation_request.environment,
        ),
        _probe_local_tool(
            _validator_tool_name(config),
            validator_request.executable,
            environment=validator_request.environment,
        ),
    ]
    required_runtimes_resolved = all(tool.available for tool in tools)
    versions_captured = all(tool.version_captured for tool in tools)
    return ConversionRuntimeEvidence(
        backend=config.backend,
        tools=tools,
        required_runtimes_resolved=required_runtimes_resolved,
        versions_captured=versions_captured,
        runtime_provenance_complete=required_runtimes_resolved and versions_captured,
        notes=notes,
    )


def _runtime_software_inventory(runtime_evidence: ConversionRuntimeEvidence) -> List[SoftwareInventoryRecord]:
    role_map = {
        "dcm2bids": "curation",
        "heudiconv": "curation",
        "dcm2niix": "conversion-dependency",
        "bids-validator-deno": "post-conversion-validation",
    }
    return [
        SoftwareInventoryRecord(
            name=tool.tool_name,
            version=tool.version,
            role=role_map.get(tool.tool_name, "runtime"),
            source=str(tool.resolved_executable) if tool.resolved_executable else None,
            container_image=tool.container_image,
        )
        for tool in runtime_evidence.tools
    ]


def _default_dataset_name(source_root: Path) -> str:
    candidate = source_root.name
    if candidate.lower() in {"in", "dicom", "source", "sourcedata"} and source_root.parent.name:
        candidate = source_root.parent.name
    return "ClawNeuro curated dataset from {0}".format(candidate)


def ensure_bids_dataset_description(bids_root: Path, source_root: Path) -> Optional[Path]:
    """Write a minimum dataset_description.json when the wrapped tool did not emit one."""

    dataset_description_path = bids_root / "dataset_description.json"
    if dataset_description_path.exists():
        return None
    dataset_description_path.write_text(
        json.dumps(
            {
                "Name": _default_dataset_name(source_root),
                "BIDSVersion": "1.10.0",
                "DatasetType": "raw",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return dataset_description_path


def cleanup_dcm2bids_temp_directory(bids_root: Path) -> bool:
    """Remove upstream temporary output that should not survive into the curated BIDS tree."""

    temp_root = bids_root / "tmp_dcm2bids"
    if not temp_root.exists():
        return False
    shutil.rmtree(temp_root)
    return True


def build_curation_request(config: DicomToBidsConfig, bids_dataset_root: Path) -> ExecutionRequest:
    """Build the Dcm2Bids or HeuDiConv command plan."""

    executable = _curation_executable(config)
    source_root = config.source_root
    output_root = bids_dataset_root
    curation_config = config.heuristic_file
    bind_mounts: List[BindMount] = []
    environment: Dict[str, str] = {}

    if config.backend != ExecutionBackend.LOCAL_BINARY:
        bind_mounts.extend(
            [
                BindMount(source=config.source_root, target=CONTAINER_INPUT_ROOT, read_only=True),
                BindMount(source=bids_dataset_root, target=CONTAINER_OUTPUT_ROOT, read_only=False),
            ]
        )
        source_root = CONTAINER_INPUT_ROOT
        output_root = CONTAINER_OUTPUT_ROOT
        if curation_config is not None:
            bind_mounts.append(
                BindMount(source=curation_config.parent, target=CONTAINER_CONFIG_ROOT, read_only=True)
            )
            curation_config = CONTAINER_CONFIG_ROOT / curation_config.name
    else:
        environment = _local_curation_environment(config)

    if config.curation_backend == CurationBackend.DCM2BIDS:
        args = ["-d", str(source_root), "-p", config.participant_label, "-o", str(output_root)]
        if config.session_label:
            args.extend(["-s", config.session_label])
        if curation_config is not None:
            args.extend(["-c", str(curation_config)])
        if config.auto_extract_entities:
            args.append("--auto_extract_entities")
        description = "Curate a public DICOM example into a BIDS tree with Dcm2Bids 3.x semantics."
    else:
        args = ["-d", str(source_root), "-s", config.participant_label, "-o", str(output_root), "-c", "dcm2niix", "-b"]
        if config.session_label:
            args.extend(["-ss", config.session_label])
        if curation_config is not None:
            args.extend(["-f", str(curation_config)])
        description = "Curate DICOM inputs with HeuDiConv using the configured heuristic."

    return ExecutionRequest(
        name=executable,
        backend=config.backend,
        executable=executable,
        args=args,
        environment=environment,
        container_image=config.conversion_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        bind_mounts=bind_mounts,
        description=description,
        use_container_entrypoint=config.backend != ExecutionBackend.LOCAL_BINARY,
    )


def _step_record(
    command: CommandRecord,
    description: str,
    artifact_paths: List[Path] | None = None,
    notes: List[str] | None = None,
) -> ExecutionStepRecord:
    log_paths = [path for path in (command.stdout_path, command.stderr_path) if path is not None]
    return ExecutionStepRecord(
        name=command.name,
        description=description,
        command=command,
        log_paths=log_paths,
        artifact_paths=artifact_paths or [],
        notes=notes or [],
    )


def _render_conversion_report(manifest: ConversionManifest) -> str:
    runtime_lines = [
        "Execution backend: `{0}`".format(manifest.runtime_evidence.backend.value),
        "Runtime provenance complete: `{0}`".format(
            str(manifest.runtime_evidence.runtime_provenance_complete).lower()
        ),
    ]
    for tool in manifest.runtime_evidence.tools:
        if tool.container_image:
            runtime_lines.append(
                "- {0}: image `{1}`".format(tool.tool_name, tool.container_image)
            )
            continue
        detail = tool.version or "version-unavailable"
        if tool.resolved_executable is not None:
            detail = "{0} ({1})".format(detail, tool.resolved_executable)
        runtime_lines.append("- {0}: {1}".format(tool.tool_name, detail))
    bundle = ReportBundleDraft(
        title="DICOM to BIDS Conversion",
        sections=[
            ReportSection(
                title="Summary",
                body="\n".join(
                    [
                        "Status: `{0}`".format(manifest.status.value),
                        "Curation backend: `{0}`".format(manifest.curation_backend.value),
                        "Participant label: `{0}`".format(manifest.participant_label),
                        "Conversion step: `{0}`".format(manifest.conversion_step.command.status.value),
                        "Validator step: `{0}`".format(manifest.validator_step.command.status.value),
                        "",
                        "Runtime evidence:",
                        *runtime_lines,
                    ]
                ),
            )
        ],
        warnings=[],
        artifact_index={},
    )
    return render_markdown_report(bundle)


def run_dicom_to_bids(config: DicomToBidsConfig) -> SkillResult:
    """Plan DICOM-to-BIDS conversion and emit a manifest-backed result."""

    input_state = detect_input_state(config.source_root)
    if input_state.kind not in {InputDatasetKind.DICOM, InputDatasetKind.UNKNOWN}:
        raise InvalidInputStateError(
            "dicom_to_bids requires a DICOM-like source directory rather than a BIDS root.",
            context={"path": str(config.source_root), "detected_kind": input_state.kind.value},
        )

    layout = ensure_run_layout(config.output_root)
    bids_dataset_root = layout.root / "bids_dataset"
    bids_dataset_root.mkdir(parents=True, exist_ok=True)

    curation_request = build_curation_request(config, bids_dataset_root)
    validator_request = build_validator_request(
        BidsAuditorConfig(
            bids_root=bids_dataset_root,
            output_root=layout.root / "post_conversion_audit",
            execute=False,
            backend=config.backend,
            container_image=config.validator_image,
            validator_executable=config.validator_executable,
            validator_config=config.validator_config,
        )
    )
    runtime_evidence = build_runtime_evidence(config, curation_request, validator_request)

    curation_stdout = layout.logs_dir / "curation.stdout.log"
    curation_stderr = layout.logs_dir / "curation.stderr.log"
    validator_stdout = layout.logs_dir / "bids-validator.stdout.log"
    validator_stderr = layout.logs_dir / "bids-validator.stderr.log"

    warnings: List[WarningRecord] = []
    if config.execute:
        curation_command = execute_request(
            curation_request,
            stdout_path=curation_stdout,
            stderr_path=curation_stderr,
        )
        if curation_command.status == RunStatus.SUCCEEDED:
            synthesized_description = ensure_bids_dataset_description(bids_dataset_root, config.source_root)
            removed_temp_directory = cleanup_dcm2bids_temp_directory(bids_dataset_root)
            if synthesized_description is not None:
                warnings.append(
                    WarningRecord(
                        code="dataset-description-synthesized",
                        severity=WarningSeverity.INFO,
                        message="A minimum dataset_description.json was synthesized before post-conversion validation.",
                        hint="Review the dataset name and metadata before external release.",
                    )
                )
            if removed_temp_directory:
                warnings.append(
                    WarningRecord(
                        code="dcm2bids-temp-removed",
                        severity=WarningSeverity.INFO,
                        message="Removed upstream tmp_dcm2bids output before post-conversion validation.",
                        hint="The temporary Dcm2Bids workspace is internal execution state and is not part of the curated BIDS dataset.",
                    )
                )
            validator_command = execute_request(
                validator_request,
                stdout_path=validator_stdout,
                stderr_path=validator_stderr,
            )
        else:
            validator_command = planned_command_record(validator_request).model_copy(
                update={
                    "status": RunStatus.SKIPPED,
                    "stdout_path": validator_stdout,
                    "stderr_path": validator_stderr,
                }
            )
            warnings.append(
                WarningRecord(
                    code="post-conversion-validation-skipped",
                    severity=WarningSeverity.WARNING,
                    message="Post-conversion validation was skipped because the curation step failed.",
                    hint="Inspect the curation logs before retrying validation.",
                )
            )
        if curation_command.status == RunStatus.SUCCEEDED and validator_command.status == RunStatus.SUCCEEDED:
            if runtime_evidence.runtime_provenance_complete:
                status = RunStatus.SUCCEEDED
            else:
                status = RunStatus.PARTIAL
                warnings.append(
                    WarningRecord(
                        code="runtime-provenance-incomplete",
                        severity=WarningSeverity.WARNING,
                        message="Conversion executed successfully, but runtime provenance is incomplete.",
                        hint="Capture resolved executable paths and stable version strings for dcm2bids, dcm2niix, and the validator before treating this run as complete.",
                    )
                )
        else:
            status = RunStatus.FAILED
    else:
        curation_command = planned_command_record(curation_request)
        validator_command = planned_command_record(validator_request)
        status = RunStatus.PLANNED
        warnings.append(
            WarningRecord(
                code="conversion-not-executed",
                severity=WarningSeverity.INFO,
                message="Conversion and post-conversion validation commands were planned but not executed.",
                hint="Re-run with execute=True after installing dcm2bids, dcm2niix, and the validator path.",
            )
        )

    unresolved_metadata: List[str] = []
    if config.heuristic_file is None:
        unresolved_metadata.append(
            "No curation config or heuristic file was supplied; execution will remain incomplete until the mapping rules are explicit."
        )
        warnings.append(
            WarningRecord(
                code="curation-config-missing",
                severity=WarningSeverity.WARNING,
                message="No curation config or heuristic file was supplied for the selected backend.",
                hint="Provide a Dcm2Bids JSON config or HeuDiConv heuristic before claiming conversion readiness.",
            )
        )
    if config.participant_mapping_file is None:
        unresolved_metadata.append(
            "No participant/session mapping file was supplied; scanner identifiers may still require manual review."
        )
    if config.curation_backend == CurationBackend.HEUDICONV:
        warnings.append(
            WarningRecord(
                code="heudiconv-not-evidence-backed",
                severity=WarningSeverity.INFO,
                message="HeuDiConv planning is supported but not evidence-backed for M3.",
                hint="M3 fidelity fixtures and benchmark notes cover Dcm2Bids only.",
            )
        )

    dataset_inventory = input_state_to_inventory(config.source_root)
    if curation_command.status == RunStatus.SUCCEEDED:
        dataset_inventory = inspect_bids_dataset(bids_dataset_root)

    conversion_manifest = ConversionManifest(
        status=status,
        bids_root=bids_dataset_root,
        curation_backend=config.curation_backend,
        participant_label=config.participant_label,
        session_label=config.session_label,
        conversion_step=_step_record(
            curation_command,
            description="Primary DICOM curation command.",
            artifact_paths=[bids_dataset_root],
        ),
        validator_step=_step_record(
            validator_command,
            description="Post-conversion BIDS validation command.",
            notes=["Validator step follows curation to surface upload-blocking issues."],
        ),
        runtime_evidence=runtime_evidence,
        unresolved_metadata=unresolved_metadata,
    )
    conversion_manifest_path = write_model_json(layout.manifests_dir / "conversion-manifest.json", conversion_manifest)
    report_path = layout.report_dir / "conversion-report.md"
    report_path.write_text(_render_conversion_report(conversion_manifest), encoding="utf-8")
    checklist_path = layout.report_dir / "curation-checklist.md"
    checklist_lines = ["# Curation Checklist", ""]
    checklist_lines.extend("- {0}".format(item) for item in unresolved_metadata)
    if not unresolved_metadata:
        checklist_lines.append("- No unresolved metadata gaps were recorded.")
    checklist_path.write_text("\n".join(checklist_lines) + "\n", encoding="utf-8")

    result = SkillResult(
        skill=SkillDescriptor(
            name="dicom_to_bids",
            kind=SkillKind.INTAKE,
            version=__version__,
            contract_path=Path("skills/dicom_to_bids/SKILL.md"),
        ),
        status=status,
        summary=(
            "Executed wrapped Dcm2Bids/HeuDiConv planning plus post-conversion validation."
            if status == RunStatus.SUCCEEDED
            else "Executed conversion, but runtime provenance remained incomplete; inspect runtime evidence before treating the run as complete."
            if status == RunStatus.PARTIAL
            else "Planned wrapped Dcm2Bids/HeuDiConv conversion plus post-conversion validation."
            if status == RunStatus.PLANNED
            else "Conversion execution failed or remained incomplete; inspect the curation logs and manifest."
        ),
        input_state=input_state,
        dataset_inventory=dataset_inventory,
        warnings=warnings,
        artifacts=[
            ArtifactRecord(
                kind=ArtifactKind.DATASET,
                path=bids_dataset_root,
                description="Target BIDS dataset root for conversion outputs.",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.MANIFEST,
                path=conversion_manifest_path,
                description="Machine-readable conversion plan and execution summary.",
                media_type="application/json",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=report_path,
                description="Human-readable DICOM-to-BIDS conversion summary.",
                media_type="text/markdown",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=checklist_path,
                description="Outstanding curation and metadata review items.",
                media_type="text/markdown",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=curation_stdout,
                description="Curation stdout log.",
                media_type="text/plain",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=curation_stderr,
                description="Curation stderr log.",
                media_type="text/plain",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=validator_stdout,
                description="Post-conversion validator stdout log.",
                media_type="text/plain",
                generated_by="dicom_to_bids",
            ),
            ArtifactRecord(
                kind=ArtifactKind.LOG,
                path=validator_stderr,
                description="Post-conversion validator stderr log.",
                media_type="text/plain",
                generated_by="dicom_to_bids",
            ),
        ],
        provenance=ProvenanceRecord(
            commands=[curation_command, validator_command],
            software=[
                SoftwareInventoryRecord(name="clawneuro", version=__version__, role="orchestration"),
                *_runtime_software_inventory(runtime_evidence),
            ],
            notes=[
                *runtime_evidence.notes,
                *[
                    "{0}: {1}".format(tool.tool_name, "; ".join(tool.notes))
                    for tool in runtime_evidence.tools
                    if tool.notes
                ],
            ],
        ),
        handoff_targets=["bids_auditor", "deid_check", "mriqc_report", "anat_bold_prep"],
        benchmark_tracks=["smoke"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=[
            "The Dcm2Bids request follows the upstream 3.x CLI contract with explicit participant, session, config, and output arguments.",
        ],
    )
    return finalized_result


def input_state_to_inventory(source_root: Path) -> DatasetInventory:
    """Represent a DICOM source as a lightweight inventory."""

    files = [path for path in source_root.rglob("*") if path.is_file()]
    return DatasetInventory(
        root=source_root,
        dataset_name=source_root.name,
        dataset_type="dicom_source",
        subject_ids=[],
        session_ids=[],
        modalities=[],
        files_by_modality={},
        file_count=len(files),
        has_dataset_description=False,
        dataset_description_path=None,
        dataset_readme_path=None,
    )
