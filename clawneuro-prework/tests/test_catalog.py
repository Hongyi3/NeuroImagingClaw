from __future__ import annotations

from pathlib import Path

import pytest

from clawneuro.catalog import (
    CatalogValidationError,
    discover_skill_specs,
    generate_catalog_data,
    validate_skill_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


def test_discover_skill_specs_tracks_foundation_prototypes() -> None:
    specs = discover_skill_specs()
    by_name = {spec.name: spec for spec in specs}

    assert by_name["neuro-orchestrator"].status == "prototype"
    assert by_name["neuro-orchestrator"].entrypoint == "skills/neuro-orchestrator/orchestrator.py"
    assert "examples/synthetic/foundation_request.json" in by_name["neuro-orchestrator"].demo_paths

    assert by_name["repro-enforcer"].status == "prototype"
    assert by_name["repro-enforcer"].entrypoint == "skills/repro-enforcer/repro_enforcer.py"
    assert "examples/synthetic/repro_seed_report.md" in by_name["repro-enforcer"].demo_paths


def test_generate_catalog_data_contains_richer_metadata() -> None:
    data = generate_catalog_data()
    skills = {entry["name"]: entry for entry in data["skills"]}

    assert data["project"] == "ClawNeuro"
    assert skills["neuro-orchestrator"]["status"] == "prototype"
    assert skills["neuro-orchestrator"]["entrypoint"] == "skills/neuro-orchestrator/orchestrator.py"
    assert skills["repro-enforcer"]["test_paths"] == [
        "tests/test_catalog.py",
        "tests/test_cli.py",
        "tests/test_provenance.py",
    ]


def test_validate_skill_metadata_rejects_nonplanned_skill_without_entrypoint(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    metadata = {
        "name": "broken-skill",
        "description": "Missing execution metadata.",
        "version": "0.1.0",
        "status": "prototype",
        "author": "Core Team",
        "license": "MIT",
        "trust_tier": "core",
        "tags": ["neuroscience"],
        "modality": "multi",
        "input_standard": ["NWB"],
        "output_standard": ["json-result"],
        "validated_with": [],
        "backends": [],
        "benchmark_ids": ["ARCH-001"],
        "trigger_keywords": ["route workflow"],
        "requires": {"python": ["python>=3.11"], "packages": [], "bins": []},
    }

    with pytest.raises(CatalogValidationError, match="entrypoint"):
        validate_skill_metadata(metadata, skill_md, benchmark_ids={"ARCH-001"})
