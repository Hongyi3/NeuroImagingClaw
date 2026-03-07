"""Configuration for the BIDS auditor skill."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator

from clawneuro.core.models import ClawBaseModel, ExecutionBackend


class BidsAuditorConfig(ClawBaseModel):
    """Typed configuration for planning or running a BIDS validation job."""

    bids_root: Path
    output_root: Path
    execute: bool = False
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    validator_executable: str = "bids-validator"
    container_image: Optional[str] = "bids/validator:latest"
    participant_labels: List[str] = Field(default_factory=list)
    policy_profile: str = "default"

    @field_validator("bids_root")
    @classmethod
    def _validate_bids_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("BIDS root does not exist.")
        return value
