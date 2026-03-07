from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def skills_dir() -> Path:
    return project_root() / "skills"


def catalog_json_path() -> Path:
    return skills_dir() / "catalog.json"


def benchmark_manifest_path() -> Path:
    return project_root() / "benchmarks" / "manifest.json"


def examples_dir() -> Path:
    return project_root() / "examples"
