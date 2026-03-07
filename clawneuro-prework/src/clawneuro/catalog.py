from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

from clawneuro.models import SkillSpec
from clawneuro.paths import catalog_json_path, project_root, skills_dir

REQUIRED_SKILL_KEYS = {
    "author",
    "backends",
    "benchmark_ids",
    "description",
    "input_standard",
    "license",
    "modality",
    "name",
    "output_standard",
    "requires",
    "status",
    "tags",
    "trigger_keywords",
    "trust_tier",
    "validated_with",
    "version",
}
OPTIONAL_SKILL_KEYS = {"demo_paths", "entrypoint", "test_paths"}
VALID_STATUSES = {"planned", "planned-phase-2", "prototype", "stable"}
VALID_MODALITIES = {"ephys", "human-ephys", "imaging", "models", "multi"}
VALID_TRUST_TIERS = {"core", "experimental", "reviewed-community"}
PLANNED_STATUSES = {"planned", "planned-phase-2"}


class CatalogValidationError(ValueError):
    """Raised when a skill manifest or catalog entry is invalid."""


def _ensure_string(value: Any, field_name: str, source: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogValidationError(f"{source}: {field_name} must be a non-empty string")
    return value.strip()


def _ensure_string_list(value: Any, field_name: str, source: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise CatalogValidationError(f"{source}: {field_name} must be a list of strings")
    items: list[str] = []
    for item in value:
        items.append(_ensure_string(item, field_name, source))
    return tuple(items)


def _ensure_mapping(value: Any, field_name: str, source: Path) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise CatalogValidationError(f"{source}: {field_name} must be a mapping")
    return value


def _ensure_relative_repo_path(path_value: str, field_name: str, source: Path) -> str:
    path = Path(path_value)
    if path.is_absolute():
        raise CatalogValidationError(f"{source}: {field_name} must be a repository-relative path")
    if ".." in path.parts:
        raise CatalogValidationError(f"{source}: {field_name} must not traverse outside the repository")
    resolved = project_root() / path
    if not resolved.exists():
        raise CatalogValidationError(f"{source}: {field_name} path does not exist: {path_value}")
    return str(path.as_posix())


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise CatalogValidationError(f"{path}: file must start with YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise CatalogValidationError(f"{path}: YAML frontmatter is not terminated")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise CatalogValidationError(f"{path}: frontmatter must parse to a mapping")
    return data


def validate_skill_metadata(
    metadata: dict[str, Any],
    skill_md_path: Path,
    *,
    benchmark_ids: Optional[set[str]] = None,
) -> SkillSpec:
    unexpected = set(metadata) - (REQUIRED_SKILL_KEYS | OPTIONAL_SKILL_KEYS)
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise CatalogValidationError(f"{skill_md_path}: unexpected frontmatter keys: {names}")

    missing = REQUIRED_SKILL_KEYS - set(metadata)
    if missing:
        names = ", ".join(sorted(missing))
        raise CatalogValidationError(f"{skill_md_path}: missing required frontmatter keys: {names}")

    status = _ensure_string(metadata["status"], "status", skill_md_path)
    if status not in VALID_STATUSES:
        raise CatalogValidationError(
            f"{skill_md_path}: status must be one of {sorted(VALID_STATUSES)}"
        )

    modality = _ensure_string(metadata["modality"], "modality", skill_md_path)
    if modality not in VALID_MODALITIES:
        raise CatalogValidationError(
            f"{skill_md_path}: modality must be one of {sorted(VALID_MODALITIES)}"
        )

    trust_tier = _ensure_string(metadata["trust_tier"], "trust_tier", skill_md_path)
    if trust_tier not in VALID_TRUST_TIERS:
        raise CatalogValidationError(
            f"{skill_md_path}: trust_tier must be one of {sorted(VALID_TRUST_TIERS)}"
        )

    entrypoint = metadata.get("entrypoint")
    if entrypoint is not None:
        entrypoint = _ensure_relative_repo_path(
            _ensure_string(entrypoint, "entrypoint", skill_md_path),
            "entrypoint",
            skill_md_path,
        )

    demo_paths = tuple(
        _ensure_relative_repo_path(path, "demo_paths", skill_md_path)
        for path in _ensure_string_list(metadata.get("demo_paths"), "demo_paths", skill_md_path)
    )
    test_paths = tuple(
        _ensure_relative_repo_path(path, "test_paths", skill_md_path)
        for path in _ensure_string_list(metadata.get("test_paths"), "test_paths", skill_md_path)
    )

    if status not in PLANNED_STATUSES:
        if not entrypoint:
            raise CatalogValidationError(
                f"{skill_md_path}: non-planned skills must declare an entrypoint"
            )
        if not demo_paths:
            raise CatalogValidationError(
                f"{skill_md_path}: non-planned skills must declare demo_paths"
            )
        if not test_paths:
            raise CatalogValidationError(
                f"{skill_md_path}: non-planned skills must declare test_paths"
            )

    spec = SkillSpec(
        name=_ensure_string(metadata["name"], "name", skill_md_path),
        description=_ensure_string(metadata["description"], "description", skill_md_path),
        version=_ensure_string(metadata["version"], "version", skill_md_path),
        status=status,
        author=_ensure_string(metadata["author"], "author", skill_md_path),
        license=_ensure_string(metadata["license"], "license", skill_md_path),
        trust_tier=trust_tier,
        tags=_ensure_string_list(metadata["tags"], "tags", skill_md_path),
        modality=modality,
        input_standard=_ensure_string_list(
            metadata["input_standard"], "input_standard", skill_md_path
        ),
        output_standard=_ensure_string_list(
            metadata["output_standard"], "output_standard", skill_md_path
        ),
        validated_with=_ensure_string_list(
            metadata["validated_with"], "validated_with", skill_md_path
        ),
        backends=_ensure_string_list(metadata["backends"], "backends", skill_md_path),
        benchmark_ids=_ensure_string_list(
            metadata["benchmark_ids"], "benchmark_ids", skill_md_path
        ),
        trigger_keywords=_ensure_string_list(
            metadata["trigger_keywords"], "trigger_keywords", skill_md_path
        ),
        requires=_ensure_mapping(metadata["requires"], "requires", skill_md_path),
        path=str(skill_md_path.relative_to(project_root()).as_posix()),
        entrypoint=entrypoint,
        demo_paths=demo_paths,
        test_paths=test_paths,
    )

    if benchmark_ids is not None:
        missing_benchmarks = sorted(set(spec.benchmark_ids) - benchmark_ids)
        if missing_benchmarks:
            raise CatalogValidationError(
                f"{skill_md_path}: unknown benchmark ids: {', '.join(missing_benchmarks)}"
            )

    return spec


def discover_skill_specs(*, benchmark_ids: Optional[set[str]] = None) -> list[SkillSpec]:
    seen_names: set[str] = set()
    specs: list[SkillSpec] = []
    for skill_md in sorted(skills_dir().glob("*/SKILL.md")):
        spec = validate_skill_metadata(parse_frontmatter(skill_md), skill_md, benchmark_ids=benchmark_ids)
        if spec.name in seen_names:
            raise CatalogValidationError(f"{skill_md}: duplicate skill name: {spec.name}")
        seen_names.add(spec.name)
        specs.append(spec)
    return sorted(specs, key=lambda item: item.name)


def generate_catalog_data() -> dict[str, Any]:
    from clawneuro.benchmarks import load_benchmark_specs

    benchmark_ids = {spec.id for spec in load_benchmark_specs()}
    skills = discover_skill_specs(benchmark_ids=benchmark_ids)
    return {
        "project": "ClawNeuro",
        "version": "0.1.0-dev",
        "generated_by": "scripts/generate_catalog.py",
        "skills": [spec.to_catalog_entry() for spec in skills],
    }


def write_catalog(path: Optional[Path] = None) -> Path:
    target = path or catalog_json_path()
    target.write_text(json.dumps(generate_catalog_data(), indent=2) + "\n", encoding="utf-8")
    return target


def load_catalog(path: Optional[Path] = None) -> dict[str, Any]:
    target = path or catalog_json_path()
    with target.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_skill_specs_from_catalog(path: Optional[Path] = None) -> list[SkillSpec]:
    catalog = load_catalog(path)
    try:
        specs = [SkillSpec.from_catalog_entry(entry) for entry in catalog.get("skills", [])]
    except KeyError:
        # Older generated catalogs may not include the richer fields now required by
        # the routing and validation layer. Fall back to the source skill manifests.
        return discover_skill_specs()
    return sorted(specs, key=lambda item: item.name)


def list_skills() -> list[dict[str, Any]]:
    return [spec.to_catalog_entry() for spec in load_skill_specs_from_catalog()]
