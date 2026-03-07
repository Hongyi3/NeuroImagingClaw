from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from clawneuro.models import BenchmarkSpec, SkillSpec
from clawneuro.paths import benchmark_manifest_path

REQUIRED_BENCHMARK_KEYS = {"id", "inputs", "name", "network_required", "stage", "success", "targets"}
VALID_BENCHMARK_STAGES = {"ci-smoke", "nightly", "phase-2", "release-qualification"}


class BenchmarkValidationError(ValueError):
    """Raised when the benchmark manifest is invalid."""


def _ensure_string(value: Any, field_name: str, source: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BenchmarkValidationError(f"{source}: {field_name} must be a non-empty string")
    return value.strip()


def _ensure_string_list(value: Any, field_name: str, source: Path) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise BenchmarkValidationError(f"{source}: {field_name} must be a non-empty list of strings")
    items: list[str] = []
    for item in value:
        items.append(_ensure_string(item, field_name, source))
    return tuple(items)


def load_benchmark_manifest(path: Optional[Path] = None) -> dict[str, Any]:
    target = path or benchmark_manifest_path()
    with target.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_benchmark_specs(
    data: dict[str, Any],
    *,
    source: Optional[Path] = None,
) -> list[BenchmarkSpec]:
    manifest_source = source or benchmark_manifest_path()
    benchmarks = data.get("benchmarks", [])
    if not isinstance(benchmarks, list) or not benchmarks:
        raise BenchmarkValidationError(
            f"{manifest_source}: benchmarks must be a non-empty list"
        )

    seen_ids: set[str] = set()
    specs: list[BenchmarkSpec] = []
    for entry in benchmarks:
        if not isinstance(entry, dict):
            raise BenchmarkValidationError(f"{manifest_source}: each benchmark must be a mapping")
        missing = REQUIRED_BENCHMARK_KEYS - set(entry)
        if missing:
            names = ", ".join(sorted(missing))
            raise BenchmarkValidationError(f"{manifest_source}: benchmark entry missing keys: {names}")

        bench_id = _ensure_string(entry["id"], "id", manifest_source)
        if bench_id in seen_ids:
            raise BenchmarkValidationError(f"{manifest_source}: duplicate benchmark id: {bench_id}")
        seen_ids.add(bench_id)

        stage = _ensure_string(entry["stage"], "stage", manifest_source)
        if stage not in VALID_BENCHMARK_STAGES:
            raise BenchmarkValidationError(
                f"{manifest_source}: stage must be one of {sorted(VALID_BENCHMARK_STAGES)}"
            )

        network_required = entry["network_required"]
        if not isinstance(network_required, bool):
            raise BenchmarkValidationError(
                f"{manifest_source}: network_required must be true or false"
            )
        if stage == "ci-smoke" and network_required:
            raise BenchmarkValidationError(
                f"{manifest_source}: ci-smoke benchmarks must be network-free"
            )

        specs.append(
            BenchmarkSpec(
                id=bench_id,
                name=_ensure_string(entry["name"], "name", manifest_source),
                stage=stage,
                network_required=network_required,
                targets=_ensure_string_list(entry["targets"], "targets", manifest_source),
                inputs=_ensure_string(entry["inputs"], "inputs", manifest_source),
                success=_ensure_string(entry["success"], "success", manifest_source),
            )
        )
    return sorted(specs, key=lambda item: item.id)


def validate_benchmark_manifest(
    *,
    path: Optional[Path] = None,
    known_skill_names: Optional[set[str]] = None,
    skill_specs: Optional[list[SkillSpec]] = None,
) -> list[BenchmarkSpec]:
    source = path or benchmark_manifest_path()
    specs = parse_benchmark_specs(load_benchmark_manifest(source), source=source)
    benchmark_ids = {spec.id for spec in specs}

    if known_skill_names is not None:
        unknown_targets = sorted(
            {
                target
                for spec in specs
                for target in spec.targets
                if target not in known_skill_names
            }
        )
        if unknown_targets:
            raise BenchmarkValidationError(
                f"{source}: unknown benchmark targets: {', '.join(unknown_targets)}"
            )

    if skill_specs is not None:
        missing_ids = {
            skill.name: sorted(set(skill.benchmark_ids) - benchmark_ids)
            for skill in skill_specs
            if set(skill.benchmark_ids) - benchmark_ids
        }
        if missing_ids:
            skill_name, unknown = next(iter(sorted(missing_ids.items())))
            raise BenchmarkValidationError(
                f"{source}: skill {skill_name} references unknown benchmark ids: {', '.join(unknown)}"
            )

    return specs


def load_benchmark_specs(path: Optional[Path] = None) -> list[BenchmarkSpec]:
    return validate_benchmark_manifest(path=path)
