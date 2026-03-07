from __future__ import annotations

import json
import shutil

import pytest

from pydantic import ValidationError

from clawneuro.core import CommandRecord, ExecutionBackend, InvalidInputStateError, RunStatus, inspect_bids_dataset
from clawneuro.skills.anat_bold_prep import (
    AnatBoldPrepConfig,
    build_anat_bold_prep_request,
    run_anat_bold_prep,
)


def test_anat_bold_prep_dry_run_writes_contract_outputs(tmp_path, fixtures_root):
    result = run_anat_bold_prep(
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "prep-plan",
            participant_labels=["01"],
            output_spaces=["MNI152NLin2009cAsym:res-2"],
        )
    )

    run_root = tmp_path / "prep-plan"
    summary_path = run_root / "manifests" / "anat-bold-prep-summary.json"
    assert result.status == RunStatus.PLANNED
    assert summary_path.exists()
    assert (run_root / "report" / "anat-bold-prep-report.md").exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["status"] == "planned"
    assert "--output-layout" in summary["command"]["argv"]
    assert "bids" in summary["command"]["argv"]


def test_anat_bold_prep_container_request_uses_stable_paths(tmp_path, fixtures_root):
    license_file = tmp_path / "license.txt"
    license_file.write_text("stub\n", encoding="utf-8")
    reuse_root = tmp_path / "reuse"
    reuse_root.mkdir()
    request = build_anat_bold_prep_request(
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "prep-run",
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/fmriprep:23.1.2",
            participant_labels=["01"],
            fs_license_file=license_file,
            freesurfer_enabled=True,
            reuse_derivative_roots=[reuse_root],
        ),
        inspect_bids_dataset(fixtures_root / "bids" / "anat_bold"),
        tmp_path / "prep-run" / "derivatives",
    )

    assert request.args[:3] == ["/clawneuro/input", "/clawneuro/output", "participant"]
    assert "--output-layout" in request.args
    assert "--work-dir" in request.args
    assert "/clawneuro/work" in request.args
    assert "--fs-license-file" in request.args
    assert "/clawneuro/license/license.txt" in request.args
    assert "--derivatives" in request.args
    assert "/clawneuro/upstream/reuse-1" in request.args
    assert {str(mount.target) for mount in request.bind_mounts} == {
        "/clawneuro/input",
        "/clawneuro/output",
        "/clawneuro/work",
        "/clawneuro/license",
        "/clawneuro/upstream/reuse-1",
    }


def test_anat_bold_prep_execute_harvests_reports_boilerplate_and_confounds(tmp_path, fixtures_root, monkeypatch):
    derivative_stub = fixtures_root / "phase2" / "fmriprep_stub"

    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("stub\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        shutil.copytree(derivative_stub, tmp_path / "prep-live" / "derivatives", dirs_exist_ok=True)
        return CommandRecord(
            name=request.name,
            backend=request.backend,
            argv=request.argv(),
            shell_command=request.shell_command(),
            status=RunStatus.SUCCEEDED,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    monkeypatch.setattr("clawneuro.skills.anat_bold_prep.runner.execute_request", fake_execute)
    result = run_anat_bold_prep(
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "prep-live",
            execute=True,
            participant_labels=["01"],
            output_spaces=["MNI152NLin2009cAsym:res-2"],
        )
    )

    summary = json.loads(
        (tmp_path / "prep-live" / "manifests" / "anat-bold-prep-summary.json").read_text(encoding="utf-8")
    )

    assert result.status == RunStatus.SUCCEEDED
    assert len(summary["report_paths"]) == 1
    assert len(summary["boilerplate_paths"]) == 2
    assert summary["confounds_file_count"] == 2


def test_anat_bold_prep_execute_returns_partial_when_boilerplate_missing(tmp_path, fixtures_root, monkeypatch):
    def fake_execute(request, stdout_path=None, stderr_path=None):
        derivative_root = tmp_path / "prep-partial" / "derivatives"
        (derivative_root / "sub-01").mkdir(parents=True, exist_ok=True)
        (derivative_root / "dataset_description.json").write_text(
            '{"Name": "Partial", "BIDSVersion": "1.10.0", "DatasetType": "derivative"}\n',
            encoding="utf-8",
        )
        (derivative_root / "sub-01.html").write_text("<html></html>\n", encoding="utf-8")
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

    monkeypatch.setattr("clawneuro.skills.anat_bold_prep.runner.execute_request", fake_execute)
    result = run_anat_bold_prep(
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "prep-partial",
            execute=True,
        )
    )

    assert result.status == RunStatus.PARTIAL
    assert any(warning.code == "anat-bold-prep-artifacts-incomplete" for warning in result.warnings)


def test_anat_bold_prep_container_execute_returns_partial_when_runtime_provenance_missing(
    tmp_path,
    fixtures_root,
    monkeypatch,
):
    derivative_stub = fixtures_root / "phase2" / "fmriprep_stub"

    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("stub\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        shutil.copytree(derivative_stub, tmp_path / "prep-container" / "derivatives", dirs_exist_ok=True)
        return CommandRecord(
            name=request.name,
            backend=request.backend,
            argv=request.argv(),
            shell_command=request.shell_command(),
            status=RunStatus.SUCCEEDED,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )

    monkeypatch.setattr("clawneuro.skills.anat_bold_prep.runner.execute_request", fake_execute)
    result = run_anat_bold_prep(
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "prep-container",
            execute=True,
            backend=ExecutionBackend.DOCKER,
            container_image="nipreps/fmriprep:23.1.2",
            participant_labels=["01"],
        )
    )

    manifest = json.loads(
        (tmp_path / "prep-container" / "manifests" / "run-manifest.json").read_text(encoding="utf-8")
    )

    assert result.status == RunStatus.PARTIAL
    assert any("docker" in note.lower() for note in manifest["provenance"]["notes"])


def test_anat_bold_prep_requires_bold_unless_anat_only(tmp_path, fixtures_root):
    with pytest.raises(InvalidInputStateError):
        run_anat_bold_prep(
            AnatBoldPrepConfig(
                bids_root=fixtures_root / "bids" / "minimal",
                output_root=tmp_path / "invalid",
            )
        )


def test_anat_bold_prep_requires_fs_license_when_freesurfer_enabled(tmp_path, fixtures_root):
    with pytest.raises(ValidationError):
        AnatBoldPrepConfig(
            bids_root=fixtures_root / "bids" / "anat_bold",
            output_root=tmp_path / "invalid",
            freesurfer_enabled=True,
        )
