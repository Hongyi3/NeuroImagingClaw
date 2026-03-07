"""Shared exception hierarchy for ClawNeuro."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ClawNeuroError(Exception):
    """Base exception with optional machine-readable context."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ConfigurationError(ClawNeuroError):
    """Raised when configuration loading or validation fails."""


class InvalidInputStateError(ClawNeuroError):
    """Raised when an input path does not match the required workflow state."""


class MissingMetadataError(ClawNeuroError):
    """Raised when required BIDS or run metadata are absent."""


class MissingToolError(ClawNeuroError):
    """Raised when a required binary or container runtime is unavailable."""


class PartialRunError(ClawNeuroError):
    """Raised when a run produced partial outputs that should not be treated as complete."""
