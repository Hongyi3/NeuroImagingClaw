from __future__ import annotations

from typer.testing import CliRunner

from clawneuro.cli import app


def test_plan_command_returns_phase1_steps(fixtures_root):
    runner = CliRunner()
    result = runner.invoke(app, ["plan", str(fixtures_root / "bids" / "minimal")])
    assert result.exit_code == 0
    assert "bids_auditor" in result.output


def test_bids_auditor_cli_writes_outputs(tmp_path, fixtures_root):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "bids-auditor",
            "--bids-root",
            str(fixtures_root / "bids" / "minimal"),
            "--output-root",
            str(tmp_path / "cli-audit"),
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "cli-audit" / "manifests" / "run-manifest.json").exists()


def test_report_bundle_cli_renders_markdown(tmp_path, fixtures_root):
    runner = CliRunner()
    audit_root = tmp_path / "cli-audit"
    runner.invoke(
        app,
        [
            "bids-auditor",
            "--bids-root",
            str(fixtures_root / "bids" / "minimal"),
            "--output-root",
            str(audit_root),
        ],
    )
    manifest_path = audit_root / "manifests" / "run-manifest.json"
    output_path = tmp_path / "bundle.md"
    result = runner.invoke(
        app,
        [
            "report-bundle",
            str(manifest_path),
            "--output-path",
            str(output_path),
        ],
    )
    assert result.exit_code == 0
    assert output_path.exists()
    assert "# ClawNeuro Execution Report" in output_path.read_text(encoding="utf-8")
