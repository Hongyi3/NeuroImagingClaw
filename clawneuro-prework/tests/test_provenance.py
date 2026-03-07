from __future__ import annotations

import json
from pathlib import Path

from clawneuro.provenance import bundle_existing_outputs, validate_bundle, write_bundle


def _relative_bundle_contents(bundle_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(bundle_dir).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(bundle_dir.rglob("*"))
        if path.is_file()
    }


def test_write_bundle_creates_required_files(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    result = write_bundle(
        bundle_dir,
        skill="neuro-orchestrator",
        status="prototype",
        report_text="# Demo\n\nFoundation bundle smoke test.",
        result_payload={"summary": {"selected_skill": "nwb-intake"}},
        extra_artifacts={"tables/route_decision.json": {"selected_skill": "nwb-intake"}},
        commands=["python clawneuro.py demo foundation --output OUTPUT_DIR"],
        random_seeds={"foundation_demo": 0},
    )

    assert result["skill"] == "neuro-orchestrator"
    assert (bundle_dir / "report.md").exists()
    assert (bundle_dir / "reproducibility" / "checksums.sha256").exists()
    assert any(artifact["path"] == "report.md" for artifact in result["artifacts"])
    validate_bundle(bundle_dir)


def test_write_bundle_is_deterministic(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    kwargs = {
        "skill": "neuro-orchestrator",
        "status": "prototype",
        "report_text": "# Demo\n\nDeterministic bundle.",
        "result_payload": {"summary": {"selected_skill": "nwb-intake"}},
        "extra_artifacts": {"tables/route_decision.json": {"selected_skill": "nwb-intake"}},
        "commands": ["python clawneuro.py demo foundation --output OUTPUT_DIR"],
        "random_seeds": {"foundation_demo": 0},
    }

    write_bundle(first_dir, **kwargs)
    write_bundle(second_dir, **kwargs)

    assert _relative_bundle_contents(first_dir) == _relative_bundle_contents(second_dir)


def test_bundle_existing_outputs_wraps_seed_fixture(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    report_path.write_text("# Existing Report\n", encoding="utf-8")
    result_path = tmp_path / "result.json"
    result_path.write_text(
        json.dumps({"skill": "seed-skill", "status": "ok", "summary": {"value": 1}}, indent=2) + "\n",
        encoding="utf-8",
    )

    bundle_dir = tmp_path / "wrapped"
    result = bundle_existing_outputs(
        report_path=report_path,
        result_path=result_path,
        output_dir=bundle_dir,
        commands=["python skills/repro-enforcer/repro_enforcer.py --report report.md --result result.json --output OUTPUT_DIR"],
        random_seeds={"repro_enforcer": 0},
    )

    assert result["skill"] == "seed-skill"
    validate_bundle(bundle_dir)
