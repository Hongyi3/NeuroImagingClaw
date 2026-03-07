from __future__ import annotations

import json

from typer.testing import CliRunner

from clawneuro.cli import app


def test_plan_command_returns_phase1_steps(fixtures_root):
    runner = CliRunner()
    result = runner.invoke(app, ["plan", str(fixtures_root / "bids" / "minimal")])
    assert result.exit_code == 0
    assert '"goal": "phase1-intake-audit"' in result.output
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


def test_dicom_to_bids_cli_renders_structured_manifest(tmp_path, fixtures_root):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "dicom-to-bids",
            "--source-root",
            str(fixtures_root / "dicom" / "source"),
            "--output-root",
            str(tmp_path / "cli-dicom"),
            "--participant-label",
            "ID01",
            "--curation-config-path",
            str(fixtures_root / "dicom" / "dcm2bids_tutorial_config.json"),
        ],
    )
    assert result.exit_code == 0
    manifest = (tmp_path / "cli-dicom" / "manifests" / "run-manifest.json").read_text(encoding="utf-8")
    assert "conversion-manifest.json" in manifest


def test_mriqc_report_cli_writes_outputs(tmp_path, fixtures_root):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "mriqc-report",
            "--bids-root",
            str(fixtures_root / "bids" / "anat_bold"),
            "--output-root",
            str(tmp_path / "cli-mriqc"),
            "--participant-label",
            "01",
            "--modality",
            "anat",
            "--modality",
            "bold",
            "--run-group",
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "cli-mriqc" / "manifests" / "mriqc-summary.json").exists()


def test_anat_bold_prep_cli_supports_config_file(tmp_path, fixtures_root):
    runner = CliRunner()
    config_path = tmp_path / "prep-config.json"
    config_path.write_text(
        json.dumps(
            {
                "bids_root": str(fixtures_root / "bids" / "anat_bold"),
                "output_root": str(tmp_path / "cli-prep"),
                "participant_labels": ["01"],
                "output_spaces": ["MNI152NLin2009cAsym:res-2"],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "anat-bold-prep",
            "--config-path",
            str(config_path),
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "cli-prep" / "manifests" / "anat-bold-prep-summary.json").exists()
