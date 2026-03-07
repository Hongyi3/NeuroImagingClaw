"""Configuration for the MRIQC reporting wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator, model_validator

from clawneuro.core.execution import is_pinned_container_image
from clawneuro.core.models import ClawBaseModel, ExecutionBackend


def _normalize_labels(values: List[str], prefix: str) -> List[str]:
    normalized = []
    for value in values:
        cleaned = value.strip()
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
        normalized.append(cleaned)
    return normalized


class MRIQCReportConfig(ClawBaseModel):
    """Typed config for planning or running MRIQC."""

    bids_root: Path
    output_root: Path
    execute: bool = False
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    mriqc_executable: str = "mriqc"
    container_image: Optional[str] = None
    participant_labels: List[str] = Field(default_factory=list)
    session_ids: List[str] = Field(default_factory=list)
    task_ids: List[str] = Field(default_factory=list)
    modalities: List[str] = Field(default_factory=list)
    nprocs: Optional[int] = None
    omp_nthreads: Optional[int] = None
    mem_gb: Optional[float] = None
    work_dir: Optional[Path] = None
    run_group: bool = False
    no_sub: bool = True

    @field_validator("bids_root")
    @classmethod
    def _validate_bids_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("BIDS root does not exist.")
        return value

    @field_validator("participant_labels")
    @classmethod
    def _normalize_participant_labels(cls, value: List[str]) -> List[str]:
        return _normalize_labels(value, "sub-")

    @field_validator("session_ids")
    @classmethod
    def _normalize_session_ids(cls, value: List[str]) -> List[str]:
        return _normalize_labels(value, "ses-")

    @field_validator("task_ids")
    @classmethod
    def _normalize_task_ids(cls, value: List[str]) -> List[str]:
        return _normalize_labels(value, "task-")

    @field_validator("modalities")
    @classmethod
    def _validate_modalities(cls, value: List[str]) -> List[str]:
        normalized = [item.lower() for item in value]
        invalid = sorted(set(normalized) - {"anat", "bold"})
        if invalid:
            raise ValueError("modalities must be limited to 'anat' and/or 'bold'.")
        return normalized

    @model_validator(mode="after")
    def _validate_backend(self) -> "MRIQCReportConfig":
        if self.backend != ExecutionBackend.LOCAL_BINARY:
            if not self.container_image:
                raise ValueError("container_image is required for Docker or Apptainer execution.")
            if not is_pinned_container_image(self.container_image):
                raise ValueError("container_image must use a pinned tag or digest, not 'latest'.")
        return self
