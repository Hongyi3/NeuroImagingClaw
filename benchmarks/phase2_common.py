"""Shared helpers for Phase 2 public benchmark drivers."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]

PHASE2_DATASET_ID = "ds003020"
PHASE2_PARTICIPANT_LABEL = "01"
MRIQC_DOCKER_IMAGE = "nipreps/mriqc:24.0.0"
FMRIPREP_DOCKER_IMAGE = "nipreps/fmriprep:23.1.2"


def backend_container_image(backend: str, docker_image: str) -> str:
    """Return the backend-appropriate pinned image reference."""

    if backend == "docker":
        return docker_image
    if backend == "apptainer":
        return docker_image if docker_image.startswith("docker://") else f"docker://{docker_image}"
    raise ValueError(f"Unsupported backend: {backend}")


def copy_run_support_dirs(run_root: Path, artifact_root: Path) -> None:
    """Copy manifest/log/report/provenance directories into the benchmark artifact root."""

    artifact_root.mkdir(parents=True, exist_ok=True)
    for name in ("manifests", "logs", "provenance", "report"):
        source = run_root / name
        destination = artifact_root / name
        if destination.exists():
            shutil.rmtree(destination)
        if source.exists():
            shutil.copytree(source, destination)


def copy_preserved_derivative_files(
    derivative_root: Path,
    artifact_root: Path,
    paths: Iterable[Path],
) -> dict[str, str]:
    """Copy selected preserved derivative artifacts into a stable benchmark subtree."""

    copied: dict[str, str] = {}
    preserved_root = artifact_root / "preserved-derivatives"
    if preserved_root.exists():
        shutil.rmtree(preserved_root)
    preserved_root.mkdir(parents=True, exist_ok=True)

    for path in sorted({candidate for candidate in paths if candidate.exists() and candidate.is_file()}):
        relative = path.relative_to(derivative_root)
        destination = preserved_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied[str(relative)] = str(destination.relative_to(artifact_root))
    return copied


def runtime_tool_index(run_manifest: Mapping[str, object]) -> dict[str, dict[str, object]]:
    """Return a name-keyed runtime/software view from a run manifest dictionary."""

    provenance = run_manifest.get("provenance", {})
    if not isinstance(provenance, dict):
        return {}
    software = provenance.get("software", [])
    if not isinstance(software, list):
        return {}

    indexed: dict[str, dict[str, object]] = {}
    for item in software:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name:
            indexed[name] = dict(item)
    return indexed


def write_benchmark_metadata(artifact_root: Path, metadata: Mapping[str, object]) -> Path:
    """Write benchmark metadata JSON with stable formatting."""

    artifact_root.mkdir(parents=True, exist_ok=True)
    metadata_path = artifact_root / "benchmark-metadata.json"
    metadata_path.write_text(
        json.dumps(dict(metadata), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata_path


def verification_command(script_name: str, *, dataset_root: str, workspace: str, artifact_root: str, backend: str) -> str:
    """Render the exact verification command recorded in benchmark metadata."""

    return (
        f"{Path(sys.executable)} benchmarks/{script_name} "
        f"--dataset-root {dataset_root} --workspace {workspace} --artifact-root {artifact_root} --backend {backend}"
    )


def benchmark_header(benchmark_id: str) -> dict[str, object]:
    """Return common metadata fields for Phase 2 benchmark runs."""

    return {
        "benchmark_id": benchmark_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_id": PHASE2_DATASET_ID,
        "participant_label": PHASE2_PARTICIPANT_LABEL,
        "notes": [],
    }
