from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clawneuro.paths import examples_dir, project_root
from clawneuro.provenance import validate_bundle, write_bundle
from clawneuro.routing import route_request


def _foundation_fixture() -> dict[str, Any]:
    fixture_path = examples_dir() / "synthetic" / "foundation_request.json"
    with fixture_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def run_foundation_demo(output_dir: Path) -> dict[str, Any]:
    fixture = _foundation_fixture()
    fixture_dir = examples_dir() / "synthetic"
    input_paths = [
        str((fixture_dir / path).relative_to(project_root()).as_posix())
        for path in fixture["input_paths"]
    ]
    decision = route_request(query=fixture["query"], input_paths=input_paths, trust_tier="core")
    if decision.selected_skill != fixture["expected_skill"]:
        raise RuntimeError(
            f"foundation demo expected {fixture['expected_skill']}, got {decision.selected_skill}"
        )

    report_lines = [
        "# Foundation Demo",
        "",
        "This synthetic demo exercises Milestone 1 routing and provenance only.",
        "",
        f"- Query: {fixture['query']}",
        f"- Inputs: {', '.join(input_paths)}",
        f"- Expected route: {fixture['expected_skill']}",
        f"- Selected route: {decision.selected_skill}",
        "",
        "No NWB parsing or DANDI access is performed in this demo. The `.nwb` fixture is routing-only.",
    ]
    result = write_bundle(
        output_dir,
        skill="neuro-orchestrator",
        status="prototype",
        report_text="\n".join(report_lines),
        result_payload={
            "summary": {
                "expected_skill": fixture["expected_skill"],
                "selected_skill": decision.selected_skill,
                "fixture": "examples/synthetic/foundation_request.json",
            },
            "request": decision.request,
            "route_decision": decision.to_dict(),
        },
        extra_artifacts={
            "tables/foundation_request.json": fixture,
            "tables/route_decision.json": decision.to_dict(),
        },
        commands=[
            "python clawneuro.py route --query \"Inspect this NWB file and summarize it for downstream routing.\" --input examples/synthetic/session_stub.nwb --json",
            "python clawneuro.py demo foundation --output OUTPUT_DIR",
        ],
        random_seeds={"foundation_demo": 0},
    )
    return validate_bundle(output_dir) or result
