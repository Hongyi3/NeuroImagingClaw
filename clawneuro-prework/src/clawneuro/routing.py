from __future__ import annotations

from pathlib import Path
from typing import Optional

from clawneuro.catalog import load_skill_specs_from_catalog
from clawneuro.models import RouteCandidate, RouteDecision, SkillSpec

TRUST_ORDER = {"core": 0, "reviewed-community": 1, "experimental": 2}
MODALITY_HINTS = {
    "ephys": {"ephys", "extracellular", "neuropixels", "recording", "spike"},
    "human-ephys": {"bids", "eeg", "ieeg", "meg", "openneuro"},
    "models": {"brian2", "model", "modeldb", "nest", "neuroml", "neuron", "pynn", "simulator"},
}
STANDARD_HINTS = {
    "bids": "BIDS",
    "dandi": "DANDI",
    "modeldb": "ModelDB",
    "neuroml": "NeuroML",
    "nwb": "NWB",
    "open source brain": "Open Source Brain",
    "openneuro": "OpenNeuro",
    "pynn": "PyNN",
}
FILE_SUFFIX_HINTS = {
    ".nwb": {"nwb-intake": 60, "spike-pipeline": 20, "spike-train-analytics": 10},
    ".nml": {"model-portability": 60},
    ".xml": {"model-portability": 40},
    ".py": {"model-reproducer": 20},
}


class RoutingError(RuntimeError):
    def __init__(self, message: str, decision: RouteDecision) -> None:
        super().__init__(message)
        self.decision = decision

    def to_dict(self) -> dict[str, object]:
        data = self.decision.to_dict()
        data["error"] = str(self)
        return data


def allowed_trust_tiers(requested_tier: str) -> set[str]:
    if requested_tier not in TRUST_ORDER:
        raise ValueError(f"unknown trust tier: {requested_tier}")
    limit = TRUST_ORDER[requested_tier]
    return {name for name, rank in TRUST_ORDER.items() if rank <= limit}


def _score_query(skill: SkillSpec, normalized_query: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    if skill.name in normalized_query:
        score += 100
        reasons.append(f"query explicitly names {skill.name}")

    for keyword in skill.trigger_keywords:
        normalized_keyword = keyword.lower()
        if normalized_keyword in normalized_query:
            score += 30
            reasons.append(f"query matches trigger keyword '{keyword}'")

    for token, standard in STANDARD_HINTS.items():
        if token in normalized_query and standard in skill.input_standard:
            score += 15
            reasons.append(f"query references {standard}")

    for modality, hints in MODALITY_HINTS.items():
        if skill.modality != modality:
            continue
        if any(hint in normalized_query for hint in hints):
            score += 10
            reasons.append(f"query suggests {modality}")
            break

    if skill.name == "neuro-orchestrator" and any(
        token in normalized_query for token in ("route", "orchestrate", "workflow")
    ):
        score += 40
        reasons.append("query asks for routing or orchestration")

    return score, reasons


def _score_inputs(skill: SkillSpec, input_paths: list[str]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    for input_path in input_paths:
        suffix = Path(input_path).suffix.lower()
        weight = FILE_SUFFIX_HINTS.get(suffix, {}).get(skill.name, 0)
        if weight:
            score += weight
            reasons.append(f"input suffix '{suffix}' maps to {skill.name}")
    return score, reasons


def route_request(
    *,
    query: str,
    input_paths: Optional[list[str]] = None,
    trust_tier: str = "core",
) -> RouteDecision:
    allowed_tiers = allowed_trust_tiers(trust_tier)
    resolved_inputs = input_paths or []
    for input_path in resolved_inputs:
        if not Path(input_path).exists():
            raise RoutingError(
                f"Input path does not exist: {input_path}",
                RouteDecision(
                    request={"query": query, "input_paths": resolved_inputs, "trust_tier": trust_tier},
                    selected_skill=None,
                    reasons=(f"Input path does not exist: {input_path}",),
                    candidates=(),
                ),
            )

    normalized_query = " ".join(query.strip().lower().split())
    request = {"query": query, "input_paths": resolved_inputs, "trust_tier": trust_tier}

    candidates: list[RouteCandidate] = []
    for skill in load_skill_specs_from_catalog():
        if skill.trust_tier not in allowed_tiers:
            continue
        score, reasons = _score_query(skill, normalized_query)
        input_score, input_reasons = _score_inputs(skill, resolved_inputs)
        score += input_score
        reasons.extend(input_reasons)
        if score > 0:
            candidates.append(
                RouteCandidate(
                    name=skill.name,
                    score=score,
                    reasons=tuple(reasons),
                    trust_tier=skill.trust_tier,
                    status=skill.status,
                )
            )

    candidates.sort(key=lambda item: (-item.score, item.name))
    if not candidates:
        decision = RouteDecision(
            request=request,
            selected_skill=None,
            reasons=("No matching skill for the provided query and inputs.",),
            candidates=(),
        )
        raise RoutingError("No matching skill for the provided query and inputs.", decision)

    if len(candidates) > 1 and candidates[0].score == candidates[1].score:
        decision = RouteDecision(
            request=request,
            selected_skill=None,
            reasons=(
                f"Routing is ambiguous between {candidates[0].name} and {candidates[1].name}.",
            ),
            candidates=tuple(candidates),
        )
        raise RoutingError(
            f"Routing is ambiguous between {candidates[0].name} and {candidates[1].name}.",
            decision,
        )

    selected = candidates[0]
    return RouteDecision(
        request=request,
        selected_skill=selected.name,
        reasons=selected.reasons,
        candidates=tuple(candidates),
    )
