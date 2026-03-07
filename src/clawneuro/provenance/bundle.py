"""Provenance and reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import yaml

from clawneuro.core.models import ArtifactRecord, CommandRecord, ProvenanceRecord, RunManifest
from clawneuro.core.layout import RunDirectoryLayout


def sha256_file(path: Path) -> str:
    """Compute a SHA256 checksum for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_checksums(paths: Iterable[Path], base_dir: Optional[Path] = None) -> Dict[str, str]:
    """Build a stable checksum mapping for existing files."""

    checksums: Dict[str, str] = {}
    for path in sorted(set(path for path in paths if path.exists() and path.is_file())):
        key = str(path.relative_to(base_dir)) if base_dir and path.is_relative_to(base_dir) else str(path)
        checksums[key] = sha256_file(path)
    return checksums


def capture_environment_snapshot() -> Dict[str, object]:
    """Capture a minimal, privacy-conscious environment snapshot."""

    safe_env = {}
    for key in ("PATH", "VIRTUAL_ENV", "CONDA_PREFIX"):
        value = os.environ.get(key)
        if value:
            safe_env[key] = value
    return {
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "safe_environment": safe_env,
    }


def write_run_manifest(path: Path, manifest: RunManifest) -> Path:
    """Write the canonical run manifest to JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.model_dump(mode="json", by_alias=True), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _write_commands_script(path: Path, commands: Sequence[CommandRecord]) -> Path:
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    for command in commands:
        lines.append("# {0} [{1}]".format(command.name, command.status.value))
        lines.append(command.shell_command)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_environment_yaml(path: Path, environment: Dict[str, object]) -> Path:
    path.write_text(yaml.safe_dump(environment, sort_keys=True, allow_unicode=False), encoding="utf-8")
    return path


def _write_analysis_log(path: Path, manifest: RunManifest, notes: Sequence[str]) -> Path:
    lines = [
        "# Analysis Log",
        "",
        "## Skill",
        manifest.skill.name,
        "",
        "## Summary",
        manifest.result_summary,
        "",
        "## Warnings",
    ]
    if manifest.warnings:
        lines.extend("- [{0}] {1}".format(item.severity.value, item.message) for item in manifest.warnings)
    else:
        lines.append("- none")
    lines.extend(["", "## Notes"])
    if notes:
        lines.extend("- {0}".format(note) for note in notes)
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_provenance_bundle(
    layout: RunDirectoryLayout,
    manifest: RunManifest,
    artifact_paths: Optional[Sequence[Path]] = None,
    notes: Optional[Sequence[str]] = None,
) -> ProvenanceRecord:
    """Write the minimum reproducibility bundle and return an updated provenance record."""

    layout.provenance_dir.mkdir(parents=True, exist_ok=True)
    commands_path = layout.provenance_dir / "commands.sh"
    environment_path = layout.provenance_dir / "environment.yml"
    analysis_log_path = layout.provenance_dir / "analysis_log.md"
    checksums_path = layout.provenance_dir / "checksums.sha256"
    manifest_path = layout.manifests_dir / "run-manifest.json"

    write_run_manifest(manifest_path, manifest)
    _write_commands_script(commands_path, manifest.provenance.commands)
    environment = capture_environment_snapshot()
    _write_environment_yaml(environment_path, environment)
    combined_notes = [*manifest.provenance.notes, *(notes or [])]
    _write_analysis_log(analysis_log_path, manifest, combined_notes)

    checksum_targets = list(artifact_paths or [])
    checksum_targets.extend([commands_path, environment_path, analysis_log_path])
    output_checksums = build_checksums(checksum_targets, base_dir=layout.root)
    checksums_path.write_text(
        "".join("{0}  {1}\n".format(digest, file_path) for file_path, digest in sorted(output_checksums.items())),
        encoding="utf-8",
    )

    return ProvenanceRecord(
        commands=manifest.provenance.commands,
        software=manifest.provenance.software,
        input_checksums=manifest.provenance.input_checksums,
        output_checksums=output_checksums,
        environment=environment,
        notes=combined_notes,
    )


def artifact_paths(artifacts: Sequence[ArtifactRecord]) -> List[Path]:
    """Extract artifact paths for checksum generation."""

    return [artifact.path for artifact in artifacts]
