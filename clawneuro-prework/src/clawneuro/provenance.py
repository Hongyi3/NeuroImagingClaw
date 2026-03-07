from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import yaml

from clawneuro.models import BundleArtifact

REQUIRED_BUNDLE_FILES = (
    "report.md",
    "result.json",
    "reproducibility/commands.sh",
    "reproducibility/environment.yml",
    "reproducibility/hardware.json",
    "reproducibility/random_seeds.json",
    "reproducibility/checksums.sha256",
)


class BundleValidationError(ValueError):
    """Raised when a reproducibility bundle is malformed."""


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _safe_relative_path(relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise BundleValidationError(f"artifact paths must be bundle-relative: {relative_path}")
    return path


def _bundle_layout(output_dir: Path) -> dict[str, Path]:
    reproducibility_dir = output_dir / "reproducibility"
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    for directory in (output_dir, reproducibility_dir, figures_dir, tables_dir):
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "root": output_dir,
        "reproducibility": reproducibility_dir,
        "figures": figures_dir,
        "tables": tables_dir,
    }


def _collect_installed_packages() -> list[str]:
    packages: list[str] = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if not name:
            continue
        packages.append(f"{name}=={distribution.version}")
    return sorted(set(packages), key=str.lower)


def _environment_yaml() -> str:
    document = {
        "name": "clawneuro-bundle",
        "channels": [],
        "dependencies": [
            f"python={platform.python_version()}",
            {"pip": _collect_installed_packages()},
        ],
    }
    return yaml.safe_dump(document, sort_keys=False)


def _hardware_snapshot() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def _category_for_path(relative_path: str) -> str:
    path = Path(relative_path)
    if relative_path == "report.md":
        return "report"
    if relative_path == "result.json":
        return "result"
    if path.parts and path.parts[0] == "figures":
        return "figure"
    if path.parts and path.parts[0] == "tables":
        return "table"
    if path.parts and path.parts[0] == "reproducibility":
        return "reproducibility"
    return "artifact"


def _artifact_entries(output_dir: Path) -> list[BundleArtifact]:
    artifacts: list[BundleArtifact] = []
    for file_path in sorted(path for path in output_dir.rglob("*") if path.is_file()):
        relative_path = file_path.relative_to(output_dir).as_posix()
        if relative_path == "reproducibility/checksums.sha256":
            continue
        artifacts.append(
            BundleArtifact(
                path=relative_path,
                category=_category_for_path(relative_path),
                size_bytes=file_path.stat().st_size,
            )
        )
    return artifacts


def _sha256_for_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_checksums(output_dir: Path, artifacts: Sequence[BundleArtifact]) -> Path:
    checksums_path = output_dir / "reproducibility" / "checksums.sha256"
    lines = [
        f"{_sha256_for_file(output_dir / artifact.path)}  {artifact.path}"
        for artifact in artifacts
    ]
    _write_text(checksums_path, "\n".join(lines))
    return checksums_path


def _write_commands(commands_path: Path, commands: Sequence[str]) -> None:
    rendered = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    if commands:
        rendered.extend(commands)
    else:
        rendered.append("# No commands were provided.")
    _write_text(commands_path, "\n".join(rendered))


def write_bundle(
    output_dir: Path,
    *,
    skill: str,
    status: str,
    report_text: str,
    result_payload: Optional[Mapping[str, Any]] = None,
    extra_artifacts: Optional[Mapping[str, Any]] = None,
    commands: Optional[Sequence[str]] = None,
    random_seeds: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    layout = _bundle_layout(output_dir)
    _write_text(layout["root"] / "report.md", report_text)

    for relative_path, payload in (extra_artifacts or {}).items():
        target = layout["root"] / _safe_relative_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, bytes):
            target.write_bytes(payload)
        elif isinstance(payload, str):
            _write_text(target, payload)
        else:
            _write_json(target, payload)

    _write_commands(layout["reproducibility"] / "commands.sh", commands or [])
    _write_text(layout["reproducibility"] / "environment.yml", _environment_yaml())
    _write_json(layout["reproducibility"] / "hardware.json", _hardware_snapshot())
    _write_json(layout["reproducibility"] / "random_seeds.json", dict(random_seeds or {}))

    reserved = {"artifacts", "reproducibility", "skill", "status"}
    merged_payload = {
        key: value for key, value in dict(result_payload or {}).items() if key not in reserved
    }

    result_path = layout["root"] / "result.json"
    _write_json(
        result_path,
        {
            "skill": skill,
            "status": status,
            **merged_payload,
            "artifacts": [],
            "reproducibility": {},
        },
    )

    artifacts = _artifact_entries(layout["root"])
    reproducibility = {
        "bundle_layout_version": "1",
        "commands": "reproducibility/commands.sh",
        "environment": "reproducibility/environment.yml",
        "hardware": "reproducibility/hardware.json",
        "random_seeds": "reproducibility/random_seeds.json",
        "checksums": "reproducibility/checksums.sha256",
    }
    _write_json(
        result_path,
        {
            "skill": skill,
            "status": status,
            **merged_payload,
            "artifacts": [artifact.to_dict() for artifact in artifacts],
            "reproducibility": reproducibility,
        },
    )

    artifacts = _artifact_entries(layout["root"])
    _write_json(
        result_path,
        {
            "skill": skill,
            "status": status,
            **merged_payload,
            "artifacts": [artifact.to_dict() for artifact in artifacts],
            "reproducibility": reproducibility,
        },
    )
    artifacts = _artifact_entries(layout["root"])
    _write_checksums(layout["root"], artifacts)
    return validate_bundle(layout["root"])


def bundle_existing_outputs(
    *,
    report_path: Path,
    result_path: Path,
    output_dir: Path,
    commands: Optional[Sequence[str]] = None,
    random_seeds: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    if not report_path.exists():
        raise BundleValidationError(f"report path does not exist: {report_path}")
    if not result_path.exists():
        raise BundleValidationError(f"result path does not exist: {result_path}")

    try:
        payload = json.loads(result_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleValidationError(f"{result_path} must contain valid JSON") from exc
    if not isinstance(payload, dict):
        raise BundleValidationError(f"{result_path} must contain a JSON object")

    skill = str(payload.get("skill", "unknown-skill"))
    status = str(payload.get("status", "bundled"))
    report_text = report_path.read_text(encoding="utf-8")
    return write_bundle(
        output_dir,
        skill=skill,
        status=status,
        report_text=report_text,
        result_payload=payload,
        commands=commands,
        random_seeds=random_seeds,
    )


def validate_bundle(output_dir: Path) -> dict[str, Any]:
    missing = [path for path in REQUIRED_BUNDLE_FILES if not (output_dir / path).exists()]
    if missing:
        raise BundleValidationError(
            f"bundle is missing required files: {', '.join(sorted(missing))}"
        )

    result_data = json.loads((output_dir / "result.json").read_text(encoding="utf-8"))
    artifacts = result_data.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        raise BundleValidationError("result.json must index generated artifacts")

    artifact_paths = []
    for artifact in artifacts:
        if not isinstance(artifact, dict) or "path" not in artifact:
            raise BundleValidationError("artifact entries must be objects with a path")
        relative_path = artifact["path"]
        artifact_paths.append(relative_path)
        if not (output_dir / relative_path).exists():
            raise BundleValidationError(f"indexed artifact does not exist: {relative_path}")

    checksums_path = output_dir / "reproducibility" / "checksums.sha256"
    checksum_lines = [
        line.strip()
        for line in checksums_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    checksum_paths = {
        line.split("  ", 1)[1]
        for line in checksum_lines
        if "  " in line
    }
    missing_checksums = sorted(set(artifact_paths) - checksum_paths)
    if missing_checksums:
        raise BundleValidationError(
            f"checksums.sha256 is missing artifact entries: {', '.join(missing_checksums)}"
        )

    return result_data
