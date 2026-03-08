from __future__ import annotations

import json
import shutil

import pytest

from pydantic import ValidationError

from clawneuro.core import (
    CommandRecord,
    ExecutionBackend,
    InvalidInputStateError,
    RunStatus,
    inspect_bids_dataset,
)
from clawneuro.skills.mriqc_report import MRIQCReportConfig, build_mriqc_participant_request, run_mriqc_report


def test_mriqc_report_dry_run_writes_contract_outputs(tmp_path, fixtures_root):
    result = run_mriqc_report(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-plan",
            participant_labels=["01"],
            modalities=["anat", "bold"],
            run_group=True,
            execute=False,
        )
    )

    run_root = tmp_path / "mriqc-plan"
    summary_path = run_root / "manifests" / "mriqc-summary.json"
    assert result.status == RunStatus.PLANNED
    assert summary_path.exists()
    assert (run_root / "report" / "mriqc-report.md").exists()
    assert (run_root / "manifests" / "run-manifest.json").exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "planned"
    assert summary["telemetry_disabled"] is True
    assert "--no-sub" in summary["participant_command"]["argv"]


def test_mriqc_report_container_request_uses_stable_paths(tmp_path, fixtures_root):
    request = build_mriqc_participant_request(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-run",
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/mriqc:24.0.0",
            participant_labels=["01"],
            modalities=["anat", "bold"],
        ),
        inventory=inspect_bids_dataset(fixtures_root / "bids" / "anat_bold"),
        derivative_root=tmp_path / "mriqc-run" / "derivatives",
    )

    assert request.args[:3] == ["/clawneuro/input", "/clawneuro/output", "participant"]
    assert "--participant-label" in request.args
    assert "-w" in request.args
    assert "/clawneuro/work" in request.args
    assert {str(mount.target) for mount in request.bind_mounts} == {
        "/clawneuro/input",
        "/clawneuro/output",
        "/clawneuro/work",
    }


def test_mriqc_report_formats_memory_without_decimal_cli_values(tmp_path, fixtures_root):
    integer_request = build_mriqc_participant_request(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-int",
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/mriqc:24.0.0",
            participant_labels=["01"],
            modalities=["anat", "bold"],
            mem_gb=12,
        ),
        inventory=inspect_bids_dataset(fixtures_root / "bids" / "anat_bold"),
        derivative_root=tmp_path / "mriqc-int" / "derivatives",
    )
    fractional_request = build_mriqc_participant_request(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-fractional",
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/mriqc:24.0.0",
            participant_labels=["01"],
            modalities=["anat", "bold"],
            mem_gb=1.5,
        ),
        inventory=inspect_bids_dataset(fixtures_root / "bids" / "anat_bold"),
        derivative_root=tmp_path / "mriqc-fractional" / "derivatives",
    )

    integer_index = integer_request.args.index("--mem_gb")
    fractional_index = fractional_request.args.index("--mem_gb")

    assert integer_request.args[integer_index + 1] == "12"
    assert fractional_request.args[fractional_index + 1] == "1500M"


def test_mriqc_report_execute_harvests_reports_and_iqms(tmp_path, fixtures_root, monkeypatch):
    derivative_stub = fixtures_root / "phase2" / "mriqc_stub"

    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("stub\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        shutil.copytree(derivative_stub, tmp_path / "mriqc-live" / "derivatives", dirs_exist_ok=True)
        return CommandRecord(
            name=request.name,
            backend=request.backend,
            argv=request.argv(),
            shell_command=request.shell_command(),
            status=RunStatus.SUCCEEDED,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    monkeypatch.setattr("clawneuro.skills.mriqc_report.runner.execute_request", fake_execute)
    result = run_mriqc_report(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-live",
            execute=True,
            run_group=True,
            participant_labels=["01"],
            modalities=["anat", "bold"],
        )
    )

    summary = json.loads(
        (tmp_path / "mriqc-live" / "manifests" / "mriqc-summary.json").read_text(encoding="utf-8")
    )

    assert result.status == RunStatus.SUCCEEDED
    assert len(summary["report_paths"]) == 2
    assert len(summary["iqm_table_paths"]) == 2
    assert summary["dataset_description_path"].endswith("dataset_description.json")


def test_mriqc_report_execute_returns_partial_when_outputs_missing(tmp_path, fixtures_root, monkeypatch):
    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("stub\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return CommandRecord(
            name=request.name,
            backend=request.backend,
            argv=request.argv(),
            shell_command=request.shell_command(),
            status=RunStatus.SUCCEEDED,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    monkeypatch.setattr("clawneuro.skills.mriqc_report.runner.execute_request", fake_execute)
    result = run_mriqc_report(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-partial",
            execute=True,
            participant_labels=["01"],
        )
    )

    assert result.status == RunStatus.PARTIAL
    assert any(warning.code == "mriqc-artifacts-incomplete" for warning in result.warnings)


def test_mriqc_report_container_execute_returns_partial_when_runtime_provenance_missing(
    tmp_path,
    fixtures_root,
    monkeypatch,
):
    derivative_stub = fixtures_root / "phase2" / "mriqc_stub"

    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("stub\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        shutil.copytree(derivative_stub, tmp_path / "mriqc-container" / "derivatives", dirs_exist_ok=True)
        return CommandRecord(
            name=request.name,
            backend=request.backend,
            argv=request.argv(),
            shell_command=request.shell_command(),
            status=RunStatus.SUCCEEDED,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    monkeypatch.setattr("clawneuro.skills.mriqc_report.runner.execute_request", fake_execute)
    result = run_mriqc_report(
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "mriqc-container",
            execute=True,
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/mriqc:24.0.0",
            run_group=True,
            participant_labels=["01"],
            modalities=["anat", "bold"],
        )
    )

    manifest = json.loads(
        (tmp_path / "mriqc-container" / "manifests" / "run-manifest.json").read_text(encoding="utf-8")
    )

    assert result.status == RunStatus.PARTIAL
    assert any("docker" in note.lower() for note in manifest["provenance"]["notes"])


def test_mriqc_report_rejects_invalid_modality_filter(tmp_path, fixtures_root):
    with pytest.raises(ValidationError):
        MRIQCReportConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "invalid",
            modalities=["dwi"],
        )


def test_mriqc_report_rejects_non_bids_input(tmp_path, fixtures_root):
    with pytest.raises(InvalidInputStateError):
        run_mriqc_report(
            MRIQCReportConfig(
                bids_root=fixtures_root / "dicom" / "source",
                output_root=tmp_path / "invalid",
            )
        )
