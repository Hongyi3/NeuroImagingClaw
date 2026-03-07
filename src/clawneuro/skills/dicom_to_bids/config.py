"""Configuration for the DICOM-to-BIDS skill."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import field_validator, model_validator

from clawneuro.core.execution import is_pinned_container_image
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
    participant_label: str = "ID01"
    session_label: Optional[str] = None
    auto_extract_entities: bool = True
    dcm2niix_executable: str = "dcm2niix"
    curation_executable: Optional[str] = None
    heuristic_file: Optional[Path] = None
    participant_mapping_file: Optional[Path] = None
    conversion_image: Optional[str] = None
    validator_image: Optional[str] = None
    validator_executable: str = "bids-validator-deno"
    validator_config: Optional[Path] = None

    @field_validator("source_root")
    @classmethod
    def _validate_source_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("Source root does not exist.")
        return value

    @field_validator("heuristic_file", "participant_mapping_file", "validator_config")
    @classmethod
    def _validate_optional_paths(cls, value: Optional[Path]) -> Optional[Path]:
        if value is not None and not value.exists():
            raise ValueError("Configured path does not exist.")
        return value

    @model_validator(mode="after")
    def _validate_container_backend(self) -> "DicomToBidsConfig":
        if self.backend != ExecutionBackend.LOCAL_BINARY:
            if not self.conversion_image:
                raise ValueError("conversion_image is required for Docker or Apptainer execution.")
            if not self.validator_image:
                raise ValueError("validator_image is required for Docker or Apptainer execution.")
            if not is_pinned_container_image(self.conversion_image):
                raise ValueError("conversion_image must use a pinned tag or digest, not 'latest'.")
            if not is_pinned_container_image(self.validator_image):
                raise ValueError("validator_image must use a pinned tag or digest, not 'latest'.")
        return self
