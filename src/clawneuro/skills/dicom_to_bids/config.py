"""Configuration for the DICOM-to-BIDS skill."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import field_validator

from clawneuro.core.models import ClawBaseModel, ExecutionBackend


class CurationBackend(str, Enum):
    """Supported curation wrappers."""

    DCM2BIDS = "dcm2bids"
    HEUDICONV = "heudiconv"


class DicomToBidsConfig(ClawBaseModel):
    """Typed config for DICOM conversion planning or execution."""

    source_root: Path
    output_root: Path
    execute: bool = False
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    curation_backend: CurationBackend = CurationBackend.DCM2BIDS
    dcm2niix_executable: str = "dcm2niix"
    curation_executable: Optional[str] = None
    heuristic_file: Optional[Path] = None
    participant_mapping_file: Optional[Path] = None
    container_image: Optional[str] = None

    @field_validator("source_root")
    @classmethod
    def _validate_source_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("Source root does not exist.")
        return value
