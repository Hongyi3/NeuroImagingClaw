"""Helpers shared across skill runtime packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from pydantic import BaseModel

from clawneuro.core.models import ArtifactKind, ArtifactRecord, RunManifest, SkillResult
from clawneuro.core.layout import RunDirectoryLayout
from clawneuro.provenance import artifact_paths as collect_artifact_paths
from clawneuro.provenance import write_provenance_bundle, write_run_manifest


def _write_config_snapshot(path: Path, config: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def provenance_artifacts(layout: RunDirectoryLayout) -> Sequence[ArtifactRecord]:
    """Return the canonical provenance artifacts for a run layout."""

    return [
        ArtifactRecord(
            kind=ArtifactKind.MANIFEST,
            path=layout.manifests_dir / "run-manifest.json",
            description="Canonical machine-readable run manifest.",
            media_type="application/json",
        ),
        ArtifactRecord(
            kind=ArtifactKind.CONFIG,
            path=layout.manifests_dir / "requested-config.json",
            description="Requested configuration snapshot for the run.",
            media_type="application/json",
        ),
        ArtifactRecord(
            kind=ArtifactKind.PROVENANCE,
            path=layout.provenance_dir / "commands.sh",
            description="Exact commands captured for this run.",
            media_type="text/x-shellscript",
        ),
        ArtifactRecord(
            kind=ArtifactKind.PROVENANCE,
            path=layout.provenance_dir / "environment.yml",
            description="Minimal environment snapshot for reproducibility.",
            media_type="text/yaml",
        ),
        ArtifactRecord(
            kind=ArtifactKind.PROVENANCE,
            path=layout.provenance_dir / "checksums.sha256",
            description="Checksums for emitted artifacts.",
            media_type="text/plain",
        ),
        ArtifactRecord(
            kind=ArtifactKind.LOG,
            path=layout.provenance_dir / "analysis_log.md",
            description="Human-readable analysis log with warnings and notes.",
            media_type="text/markdown",
        ),
    ]


def finalize_skill_result(
    layout: RunDirectoryLayout,
    result: SkillResult,
    requested_config: BaseModel,
    notes: Optional[Sequence[str]] = None,
) -> Tuple[SkillResult, RunManifest]:
    """Write config, provenance, and manifest artifacts for a skill result."""

    config_data = requested_config.model_dump(mode="json")
    config_path = _write_config_snapshot(layout.manifests_dir / "requested-config.json", config_data)
    current_artifacts = list(result.artifacts)
    current_artifacts.extend(provenance_artifacts(layout))
    result.artifacts = current_artifacts

    initial_manifest = RunManifest.from_result(result, requested_config=config_data)
    provenance = write_provenance_bundle(
        layout=layout,
        manifest=initial_manifest,
        artifact_paths=collect_artifact_paths(result.artifacts) + [config_path],
        notes=notes or [],
    )
    result.provenance = provenance

    final_manifest = RunManifest.from_result(result, requested_config=config_data)
    write_run_manifest(layout.manifests_dir / "run-manifest.json", final_manifest)
    return result, final_manifest
