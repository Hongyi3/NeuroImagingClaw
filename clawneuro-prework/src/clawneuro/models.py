from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    version: str
    status: str
    author: str
    license: str
    trust_tier: str
    tags: tuple[str, ...]
    modality: str
    input_standard: tuple[str, ...]
    output_standard: tuple[str, ...]
    validated_with: tuple[str, ...]
    backends: tuple[str, ...]
    benchmark_ids: tuple[str, ...]
    trigger_keywords: tuple[str, ...]
    requires: dict[str, Any]
    path: str
    entrypoint: Optional[str] = None
    demo_paths: tuple[str, ...] = ()
    test_paths: tuple[str, ...] = ()

    def to_catalog_entry(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "author": self.author,
            "license": self.license,
            "trust_tier": self.trust_tier,
            "tags": list(self.tags),
            "modality": self.modality,
            "input_standard": list(self.input_standard),
            "output_standard": list(self.output_standard),
            "validated_with": list(self.validated_with),
            "backends": list(self.backends),
            "benchmark_ids": list(self.benchmark_ids),
            "trigger_keywords": list(self.trigger_keywords),
            "requires": self.requires,
            "path": self.path,
            "entrypoint": self.entrypoint,
            "demo_paths": list(self.demo_paths),
            "test_paths": list(self.test_paths),
        }

    @classmethod
    def from_catalog_entry(cls, entry: dict[str, Any]) -> "SkillSpec":
        return cls(
            name=entry["name"],
            description=entry["description"],
            version=entry["version"],
            status=entry["status"],
            author=entry["author"],
            license=entry["license"],
            trust_tier=entry["trust_tier"],
            tags=tuple(entry.get("tags", [])),
            modality=entry["modality"],
            input_standard=tuple(entry.get("input_standard", [])),
            output_standard=tuple(entry.get("output_standard", [])),
            validated_with=tuple(entry.get("validated_with", [])),
            backends=tuple(entry.get("backends", [])),
            benchmark_ids=tuple(entry.get("benchmark_ids", [])),
            trigger_keywords=tuple(entry.get("trigger_keywords", [])),
            requires=dict(entry.get("requires", {})),
            path=entry["path"],
            entrypoint=entry.get("entrypoint"),
            demo_paths=tuple(entry.get("demo_paths", [])),
            test_paths=tuple(entry.get("test_paths", [])),
        )


@dataclass(frozen=True)
class BenchmarkSpec:
    id: str
    name: str
    stage: str
    network_required: bool
    targets: tuple[str, ...]
    inputs: str
    success: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "stage": self.stage,
            "network_required": self.network_required,
            "targets": list(self.targets),
            "inputs": self.inputs,
            "success": self.success,
        }


@dataclass(frozen=True)
class RouteCandidate:
    name: str
    score: int
    reasons: tuple[str, ...]
    trust_tier: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "reasons": list(self.reasons),
            "trust_tier": self.trust_tier,
            "status": self.status,
        }


@dataclass(frozen=True)
class RouteDecision:
    request: dict[str, Any]
    selected_skill: Optional[str]
    reasons: tuple[str, ...] = ()
    candidates: tuple[RouteCandidate, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "selected_skill": self.selected_skill,
            "reasons": list(self.reasons),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


@dataclass(frozen=True)
class BundleArtifact:
    path: str
    category: str
    size_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "category": self.category,
            "size_bytes": self.size_bytes,
        }
