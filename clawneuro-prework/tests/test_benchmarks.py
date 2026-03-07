from __future__ import annotations

import pytest

from clawneuro.benchmarks import BenchmarkValidationError, validate_benchmark_manifest
from clawneuro.catalog import discover_skill_specs
from clawneuro.models import SkillSpec


def test_validate_benchmark_manifest_accepts_repo_manifest() -> None:
    skill_specs = discover_skill_specs()
    specs = validate_benchmark_manifest(
        known_skill_names={skill.name for skill in skill_specs},
        skill_specs=skill_specs,
    )
    ids = {spec.id for spec in specs}
    assert {"ARCH-001", "REPORT-001", "REPRO-001"} <= ids


def test_validate_benchmark_manifest_rejects_unknown_target(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        """
        {
          "version": "0.1.0-dev",
          "policy": {},
          "benchmarks": [
            {
              "id": "ARCH-999",
              "name": "Broken target",
              "stage": "ci-smoke",
              "network_required": false,
              "targets": ["does-not-exist"],
              "inputs": "Synthetic",
              "success": "Should fail"
            }
          ]
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(BenchmarkValidationError, match="unknown benchmark targets"):
        validate_benchmark_manifest(path=path, known_skill_names={"nwb-intake"})


def test_validate_benchmark_manifest_rejects_ci_smoke_network_dependency(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        """
        {
          "version": "0.1.0-dev",
          "policy": {},
          "benchmarks": [
            {
              "id": "ARCH-998",
              "name": "Networked smoke",
              "stage": "ci-smoke",
              "network_required": true,
              "targets": ["nwb-intake"],
              "inputs": "Synthetic",
              "success": "Should fail"
            }
          ]
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(BenchmarkValidationError, match="ci-smoke benchmarks must be network-free"):
        validate_benchmark_manifest(path=path, known_skill_names={"nwb-intake"})


def test_validate_benchmark_manifest_rejects_missing_skill_benchmark_reference(tmp_path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        """
        {
          "version": "0.1.0-dev",
          "policy": {},
          "benchmarks": [
            {
              "id": "ARCH-997",
              "name": "Known benchmark",
              "stage": "ci-smoke",
              "network_required": false,
              "targets": ["nwb-intake"],
              "inputs": "Synthetic",
              "success": "Should pass"
            }
          ]
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )
    broken_skill = SkillSpec(
        name="broken-skill",
        description="Broken benchmark reference",
        version="0.1.0",
        status="planned",
        author="Core Team",
        license="MIT",
        trust_tier="core",
        tags=("neuroscience",),
        modality="multi",
        input_standard=("NWB",),
        output_standard=("json-result",),
        validated_with=(),
        backends=(),
        benchmark_ids=("DOES-NOT-EXIST",),
        trigger_keywords=("broken",),
        requires={},
        path="skills/broken-skill/SKILL.md",
    )

    with pytest.raises(BenchmarkValidationError, match="references unknown benchmark ids"):
        validate_benchmark_manifest(
            path=path,
            known_skill_names={"nwb-intake"},
            skill_specs=[broken_skill],
        )
