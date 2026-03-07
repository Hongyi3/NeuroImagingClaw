"""Configuration for the de-identification readiness skill."""

from __future__ import annotations

from pathlib import Path

from pydantic import field_validator

from clawneuro.core.models import ClawBaseModel


class DeidCheckConfig(ClawBaseModel):
    """Typed config for local privacy-readiness checks."""

    bids_root: Path
    output_root: Path
    policy_profile: str = "openneuro"

    @field_validator("bids_root")
    @classmethod
    def _validate_bids_root(cls, value: Path) -> Path:
        if not value.exists():
            raise ValueError("BIDS root does not exist.")
        return value
