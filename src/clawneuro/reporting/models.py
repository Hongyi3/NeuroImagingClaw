"""Models used by deterministic reporting helpers."""

from __future__ import annotations

from typing import Dict, List

from pydantic import Field

from clawneuro.core.models import ArtifactRecord, ClawBaseModel, WarningRecord


class ReportSection(ClawBaseModel):
    """Single report section."""

    title: str
    body: str
    warnings: List[WarningRecord] = Field(default_factory=list)
    artifacts: List[ArtifactRecord] = Field(default_factory=list)


class ReportBundleDraft(ClawBaseModel):
    """Structured report draft prior to HTML/PDF rendering."""

    title: str
    sections: List[ReportSection] = Field(default_factory=list)
    warnings: List[WarningRecord] = Field(default_factory=list)
    artifact_index: Dict[str, List[str]] = Field(default_factory=dict)
