"""Configuration for the anat + BOLD preprocessing wrapper."""

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


class AnatBoldPrepConfig(ClawBaseModel):
    """Typed config for planning or running fMRIPrep-family preprocessing."""

    bids_root: Path
    output_root: Path
    execute: bool = False
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    fmriprep_executable: str = "fmriprep"
    container_image: Optional[str] = None
    participant_labels: List[str] = Field(default_factory=list)
    anat_only: bool = False
    output_layout: str = "bids"
    output_spaces: List[str] = Field(default_factory=list)
    work_dir: Optional[Path] = None
    fs_license_file: Optional[Path] = None
    reuse_derivative_roots: List[Path] = Field(default_factory=list)
    nprocs: Optional[int] = None
    omp_nthreads: Optional[int] = None
    mem_mb: Optional[int] = None
    notrack: bool = True
    freesurfer_enabled: bool = False

    @field_validator("bids_root")
    @classmethod
    def _validate_bids_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("BIDS root does not exist.")
        return value

    @field_validator("participant_labels")
    @classmethod
    def _normalize_participants(cls, value: List[str]) -> List[str]:
        return _normalize_labels(value, "sub-")

    @field_validator("fs_license_file")
    @classmethod
    def _validate_fs_license_file(cls, value: Optional[Path]) -> Optional[Path]:
        if value is not None and not value.exists():
            raise ValueError("fs_license_file does not exist.")
        return value

    @field_validator("reuse_derivative_roots")
    @classmethod
    def _validate_reuse_derivatives(cls, value: List[Path]) -> List[Path]:
        for path in value:
            if not path.exists():
                raise ValueError("Configured reuse_derivative_roots path does not exist.")
        return value

    @field_validator("output_layout")
    @classmethod
    def _validate_output_layout(cls, value: str) -> str:
        if value != "bids":
            raise ValueError("output_layout must remain 'bids' for the Phase 2 baseline.")
        return value

    @model_validator(mode="after")
    def _validate_backend(self) -> "AnatBoldPrepConfig":
        if self.backend != ExecutionBackend.LOCAL_BINARY:
            if not self.container_image:
                raise ValueError("container_image is required for Docker or Apptainer execution.")
            if not is_pinned_container_image(self.container_image):
                raise ValueError("container_image must use a pinned tag or digest, not 'latest'.")
        if self.freesurfer_enabled and self.fs_license_file is None:
            raise ValueError("fs_license_file is required when freesurfer_enabled is true.")
        return self
