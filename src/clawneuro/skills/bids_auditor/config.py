"""Configuration for the BIDS auditor skill."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator, model_validator

from clawneuro.core.execution import is_pinned_container_image
from clawneuro.core.models import ClawBaseModel, ExecutionBackend


class BidsAuditorConfig(ClawBaseModel):
    """Typed configuration for planning or running a BIDS validation job."""

    bids_root: Path
    output_root: Path
    execute: bool = False
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    validator_executable: str = "bids-validator-deno"
    container_image: Optional[str] = None
    validator_config: Optional[Path] = None
    validator_format: str = "json"
    participant_labels: List[str] = Field(default_factory=list)
    policy_profile: str = "default"

    @field_validator("bids_root")
    @classmethod
    def _validate_bids_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("BIDS root does not exist.")
        return value

    @field_validator("validator_config")
    @classmethod
    def _validate_validator_config(cls, value: Optional[Path]) -> Optional[Path]:
        if value is not None and not value.exists():
            raise ValueError("Validator config path does not exist.")
        return value

    @field_validator("validator_format")
    @classmethod
    def _validate_validator_format(cls, value: str) -> str:
        if value not in {"json", "json_pp"}:
            raise ValueError("validator_format must be 'json' or 'json_pp'.")
        return value

    @model_validator(mode="after")
    def _validate_container_backend(self) -> "BidsAuditorConfig":
        if self.backend != ExecutionBackend.LOCAL_BINARY:
            if not self.container_image:
                raise ValueError("container_image is required for Docker or Apptainer execution.")
            if not is_pinned_container_image(self.container_image):
                raise ValueError("container_image must use a pinned tag or digest, not 'latest'.")
        return self
