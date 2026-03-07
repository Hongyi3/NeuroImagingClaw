from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_list_smoke() -> None:
    result = _run("clawneuro.py", "list")
    assert result.returncode == 0
    assert "neuro-orchestrator" in result.stdout
    assert "[prototype]" in result.stdout


def test_cli_show_smoke() -> None:
    result = _run("clawneuro.py", "show", "neuro-orchestrator")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["entrypoint"] == "skills/neuro-orchestrator/orchestrator.py"


def test_cli_route_smoke() -> None:
    result = _run(
        "clawneuro.py",
        "route",
        "--query",
        "Inspect this NWB file and summarize it for downstream routing.",
        "--input",
        "examples/synthetic/session_stub.nwb",
        "--json",
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["selected_skill"] == "nwb-intake"


def test_cli_foundation_demo_smoke(tmp_path: Path) -> None:
    output_dir = tmp_path / "foundation-demo"
    result = _run("clawneuro.py", "demo", "foundation", "--output", str(output_dir))
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["selected_skill"] == "nwb-intake"
    assert (output_dir / "reproducibility" / "checksums.sha256").exists()


def test_repro_enforcer_entrypoint_smoke(tmp_path: Path) -> None:
    output_dir = tmp_path / "repro-bundle"
    result = _run(
        "skills/repro-enforcer/repro_enforcer.py",
        "--report",
        "examples/synthetic/repro_seed_report.md",
        "--result",
        "examples/synthetic/repro_seed_result.json",
        "--output",
        str(output_dir),
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["skill"] == "synthetic-fixture"
    assert (output_dir / "result.json").exists()
