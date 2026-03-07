from __future__ import annotations

from pathlib import Path

import pytest

from clawneuro.routing import RoutingError, route_request

ROOT = Path(__file__).resolve().parents[1]


def test_route_request_prefers_nwb_intake_for_synthetic_fixture() -> None:
    fixture = ROOT / "examples" / "synthetic" / "session_stub.nwb"
    decision = route_request(
        query="Inspect this NWB file and summarize it for downstream routing.",
        input_paths=[str(fixture)],
    )

    assert decision.selected_skill == "nwb-intake"
    assert decision.candidates[0].name == "nwb-intake"


def test_route_request_matches_explicit_skill_name() -> None:
    decision = route_request(
        query="Use repro-enforcer to export checksums and environment metadata.",
        input_paths=[],
    )

    assert decision.selected_skill == "repro-enforcer"


def test_route_request_rejects_missing_input_path() -> None:
    with pytest.raises(RoutingError, match="Input path does not exist"):
        route_request(query="Inspect this NWB file.", input_paths=["missing_fixture.nwb"])


def test_route_request_rejects_ambiguous_queries() -> None:
    with pytest.raises(RoutingError, match="ambiguous"):
        route_request(query="nwb", input_paths=[])


def test_route_request_rejects_no_match() -> None:
    with pytest.raises(RoutingError, match="No matching skill"):
        route_request(query="galaxy cluster lensing", input_paths=[])
