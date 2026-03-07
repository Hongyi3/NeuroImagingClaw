"""Typed contracts shared across skills, orchestration, and reporting."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClawBaseModel(BaseModel):
    """Base model with strict validation and deterministic serialization."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)


class RunStatus(str, Enum):
    """Lifecycle state for runs and skill results."""

    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class SkillKind(str, Enum):
    """High-level skill taxonomy."""

    INTAKE = "intake"
    AUDIT = "audit"
    PRIVACY = "privacy"
    QC = "qc"
    PREPROCESSING = "preprocessing"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    PROVENANCE = "provenance"
    ORCHESTRATION = "orchestration"


class InputDatasetKind(str, Enum):
    """Supported repository entry states."""

    BIDS = "bids"
    DICOM = "dicom"
    DERIVATIVE = "derivative"
    UNKNOWN = "unknown"


class ArtifactKind(str, Enum):
    """Categories used in manifests and reports."""

    REPORT = "report"
    MANIFEST = "manifest"
    LOG = "log"
    PROVENANCE = "provenance"
    DERIVATIVE = "derivative"
    DATASET = "dataset"
    SUMMARY = "summary"
    TABLE = "table"
    CONFIG = "config"
    METADATA = "metadata"


class WarningSeverity(str, Enum):
    """Severity levels surfaced in reports and manifests."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ExecutionBackend(str, Enum):
    """Supported execution backends for wrapped tools."""

    LOCAL_BINARY = "local_binary"
    DOCKER = "docker"
    APPTAINER = "apptainer"


class WarningRecord(ClawBaseModel):
    """Structured warning or blocker."""

    code: str
    severity: WarningSeverity
    message: str
    hint: Optional[str] = None


class ArtifactRecord(ClawBaseModel):
    """Machine-readable description of an emitted artifact."""

    kind: ArtifactKind
    path: Path
    description: str
    media_type: Optional[str] = None
    generated_by: Optional[str] = None


class SkillInputState(ClawBaseModel):
    """Normalized description of an input path before execution."""

    root: Path
    kind: InputDatasetKind
    readable: bool
    dataset_description_present: bool = False
    contains_dicom: bool = False
    modalities: List[str] = Field(default_factory=list)
    participant_ids: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class DatasetInventory(ClawBaseModel):
    """Summary of a raw or derivative dataset used for manifests and reports."""

    root: Path
    dataset_name: str
    dataset_type: str = "raw"
    subject_ids: List[str] = Field(default_factory=list)
    session_ids: List[str] = Field(default_factory=list)
    modalities: List[str] = Field(default_factory=list)
    files_by_modality: Dict[str, int] = Field(default_factory=dict)
    file_count: int = 0
    has_dataset_description: bool = False
    dataset_description_path: Optional[Path] = None
    dataset_readme_path: Optional[Path] = None


class SoftwareInventoryRecord(ClawBaseModel):
    """Software package or tool recorded in provenance."""

    name: str
    version: Optional[str] = None
    role: Optional[str] = None
    source: Optional[str] = None
    container_image: Optional[str] = None
    container_digest: Optional[str] = None


class CommandRecord(ClawBaseModel):
    """Recorded command invocation or planned command."""

    name: str
    backend: ExecutionBackend
    argv: List[str]
    shell_command: str
    working_directory: Optional[Path] = None
    environment: Dict[str, str] = Field(default_factory=dict)
    status: RunStatus = RunStatus.PLANNED
    exit_code: Optional[int] = None
    stdout_path: Optional[Path] = None
    stderr_path: Optional[Path] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class ProvenanceRecord(ClawBaseModel):
    """Minimum provenance required to justify a completed run."""

    commands: List[CommandRecord] = Field(default_factory=list)
    software: List[SoftwareInventoryRecord] = Field(default_factory=list)
    input_checksums: Dict[str, str] = Field(default_factory=dict)
    output_checksums: Dict[str, str] = Field(default_factory=dict)
    environment: Dict[str, Any] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


class SkillDescriptor(ClawBaseModel):
    """Identity and type metadata for a skill."""

    name: str
    kind: SkillKind
    version: str = "0.1.0"
    contract_path: Optional[Path] = None


class SkillResult(ClawBaseModel):
    """Stable execution result returned by skills."""

    skill: SkillDescriptor
    status: RunStatus
    summary: str
    input_state: SkillInputState
    dataset_inventory: DatasetInventory
    warnings: List[WarningRecord] = Field(default_factory=list)
    artifacts: List[ArtifactRecord] = Field(default_factory=list)
    provenance: ProvenanceRecord = Field(default_factory=ProvenanceRecord)
    handoff_targets: List[str] = Field(default_factory=list)
    benchmark_tracks: List[str] = Field(default_factory=list)


class RunManifest(ClawBaseModel):
    """Deterministic machine-readable run manifest."""

    schema_version: str = "0.1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    clawneuro_version: str = "0.1.0"
    skill: SkillDescriptor
    status: RunStatus
    input_state: SkillInputState
    dataset_inventory: DatasetInventory
    requested_config: Dict[str, Any] = Field(default_factory=dict)
    result_summary: str
    warnings: List[WarningRecord] = Field(default_factory=list)
    artifacts: List[ArtifactRecord] = Field(default_factory=list)
    provenance: ProvenanceRecord = Field(default_factory=ProvenanceRecord)
    handoff_targets: List[str] = Field(default_factory=list)
    benchmark_tracks: List[str] = Field(default_factory=list)

    @classmethod
    def from_result(
        cls,
        result: SkillResult,
        requested_config: Optional[Dict[str, Any]] = None,
    ) -> "RunManifest":
        """Create a manifest directly from a skill result."""

        return cls(
            skill=result.skill,
            status=result.status,
            input_state=result.input_state,
            dataset_inventory=result.dataset_inventory,
            requested_config=requested_config or {},
            result_summary=result.summary,
            warnings=result.warnings,
            artifacts=result.artifacts,
            provenance=result.provenance,
            handoff_targets=result.handoff_targets,
            benchmark_tracks=result.benchmark_tracks,
        )


class GeneratedByRecord(ClawBaseModel):
    """BIDS Derivatives GeneratedBy entry."""

    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    container: Dict[str, str] = Field(default_factory=dict)


class DerivativeDatasetDescription(ClawBaseModel):
    """Minimal BIDS Derivatives dataset description helper."""

    name: str = Field(alias="Name")
    bids_version: str = Field(default="1.10.0", alias="BIDSVersion")
    dataset_type: str = Field(default="derivative", alias="DatasetType")
    generated_by: List[GeneratedByRecord] = Field(default_factory=list, alias="GeneratedBy")
    source_datasets: List[Dict[str, str]] = Field(default_factory=list, alias="SourceDatasets")
