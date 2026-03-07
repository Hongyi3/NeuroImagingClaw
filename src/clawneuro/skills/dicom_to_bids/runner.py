"""Runner for the DICOM-to-BIDS skill."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    CommandRecord,
    ExecutionBackend,
    ExecutionRequest,
    DatasetInventory,
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
    planned_command_record,
)
from clawneuro.core.config import write_model_json
from clawneuro.core.models import ClawBaseModel, ProvenanceRecord
from clawneuro.reporting import render_markdown_report
from clawneuro.reporting.models import ReportBundleDraft, ReportSection
from clawneuro.skills.common import finalize_skill_result
from clawneuro.skills.dicom_to_bids.config import CurationBackend, DicomToBidsConfig
from clawneuro.skills.bids_auditor.config import BidsAuditorConfig
from clawneuro.skills.bids_auditor.runner import build_validator_request


class PlannedToolStep(ClawBaseModel):
    """A single planned conversion step."""

    name: str
    backend: str
    command: str


class ConversionManifest(ClawBaseModel):
    """Machine-readable summary of the planned or executed conversion workflow."""

    status: RunStatus
    bids_root: Path
    curation_backend: CurationBackend
    planned_steps: List[PlannedToolStep] = Field(default_factory=list)
    unresolved_metadata: List[str] = Field(default_factory=list)


def _curation_executable(config: DicomToBidsConfig) -> str:
    if config.curation_executable:
        return config.curation_executable
    return "dcm2bids" if config.curation_backend == CurationBackend.DCM2BIDS else "heudiconv"


def build_dcm2niix_request(config: DicomToBidsConfig, bids_dataset_root: Path) -> ExecutionRequest:
    """Build the dcm2niix command plan."""

    args = ["-o", str(bids_dataset_root / "sourcedata" / "nifti-staging"), str(config.source_root)]
    return ExecutionRequest(
        name="dcm2niix",
        backend=config.backend,
        executable=config.dcm2niix_executable,
        args=args,
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        description="Convert DICOM inputs to NIfTI plus sidecars for later BIDS curation.",
    )


def build_curation_request(config: DicomToBidsConfig, bids_dataset_root: Path) -> ExecutionRequest:
    """Build the HeuDiConv or Dcm2Bids command plan."""

    executable = _curation_executable(config)
    args = ["--output-dir", str(bids_dataset_root)]
    if config.heuristic_file:
        args.extend(["--heuristic", str(config.heuristic_file)])
    if config.participant_mapping_file:
        args.extend(["--participant-mapping", str(config.participant_mapping_file)])
    return ExecutionRequest(
        name=executable,
        backend=config.backend,
        executable=executable,
        args=args,
        container_image=config.container_image if config.backend != ExecutionBackend.LOCAL_BINARY else None,
        description="Curate converted inputs into a BIDS dataset tree.",
    )


def _render_conversion_report(manifest: ConversionManifest) -> str:
    bundle = ReportBundleDraft(
        title="DICOM to BIDS Conversion",
        sections=[
            ReportSection(
                title="Summary",
                body="\n".join(
                    [
                        "Status: `{0}`".format(manifest.status.value),
                        "Planned steps: {0}".format(len(manifest.planned_steps)),
                        "Curation backend: `{0}`".format(manifest.curation_backend.value),
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

    dcm2niix_request = build_dcm2niix_request(config, bids_dataset_root)
    curation_request = build_curation_request(config, bids_dataset_root)
    validator_request = build_validator_request(
        BidsAuditorConfig(
            bids_root=bids_dataset_root,
            output_root=layout.root / "post_conversion_audit",
            execute=False,
            backend=config.backend,
            container_image=config.container_image,
        )
    )
    commands: List[CommandRecord] = []

    status = RunStatus.PLANNED
    warnings = []
    if config.execute:
        commands.append(
            execute_request(
                dcm2niix_request,
                stdout_path=layout.logs_dir / "dcm2niix.stdout.log",
                stderr_path=layout.logs_dir / "dcm2niix.stderr.log",
            )
        )
        commands.append(
            execute_request(
                curation_request,
                stdout_path=layout.logs_dir / "curation.stdout.log",
                stderr_path=layout.logs_dir / "curation.stderr.log",
            )
        )
        commands.append(
            execute_request(
                validator_request,
                stdout_path=layout.logs_dir / "bids-validator.stdout.log",
                stderr_path=layout.logs_dir / "bids-validator.stderr.log",
            )
        )
        status = (
            RunStatus.SUCCEEDED
            if all(command.status == RunStatus.SUCCEEDED for command in commands)
            else RunStatus.FAILED
        )
    else:
        commands.extend(
            [
                planned_command_record(dcm2niix_request),
                planned_command_record(curation_request),
                planned_command_record(validator_request),
            ]
        )
        warnings.append(
            WarningRecord(
                code="conversion-not-executed",
                severity=WarningSeverity.INFO,
                message="Conversion and post-conversion validation commands were planned but not executed.",
                hint="Re-run with execute=True after installing dcm2niix and the chosen curation tool.",
            )
        )
    unresolved_metadata = []
    if config.heuristic_file is None:
        unresolved_metadata.append(
            "No heuristic or mapping file was supplied; curation details must be reviewed before execution."
        )
    if config.participant_mapping_file is None:
        unresolved_metadata.append(
            "No participant/session mapping file was supplied; scanner identifiers may need manual review."
        )

    conversion_manifest = ConversionManifest(
        status=status,
        bids_root=bids_dataset_root,
        curation_backend=config.curation_backend,
        planned_steps=[
            PlannedToolStep(
                name=command.name,
                backend=command.backend.value,
                command=command.shell_command,
            )
            for command in commands
        ],
        unresolved_metadata=unresolved_metadata,
    )
    conversion_manifest_path = write_model_json(layout.manifests_dir / "conversion-manifest.json", conversion_manifest)
    report_path = layout.report_dir / "conversion-report.md"
    report_path.write_text(_render_conversion_report(conversion_manifest), encoding="utf-8")
    checklist_path = layout.report_dir / "curation-checklist.md"
    checklist_lines = ["# Curation Checklist", ""] + [
        "- {0}".format(item) for item in unresolved_metadata
    ]
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
            "Executed wrapped dcm2niix, curation, and post-conversion validation commands."
            if status == RunStatus.SUCCEEDED
            else "Planned wrapped dcm2niix, curation, and post-conversion validation commands."
        ),
        input_state=input_state,
        dataset_inventory=input_state_to_inventory(config.source_root),
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
                description="Machine-readable conversion plan and unresolved metadata checklist.",
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
        ],
        provenance=ProvenanceRecord(
            commands=commands,
            software=[
                SoftwareInventoryRecord(name="clawneuro", version=__version__, role="orchestration"),
                SoftwareInventoryRecord(name=config.dcm2niix_executable, role="conversion"),
                SoftwareInventoryRecord(name=_curation_executable(config), role="curation"),
            ],
        ),
        handoff_targets=["bids_auditor", "deid_check", "mriqc_report", "anat_bold_prep"],
        benchmark_tracks=["smoke"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=["Conversion planning is deterministic given the captured config and source path."],
    )
    return finalized_result


def input_state_to_inventory(source_root: Path):
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
