from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from pydantic import ValidationError

from clawneuro.core import ExecutionBackend
from clawneuro.skills.dicom_to_bids import DicomToBidsConfig, run_dicom_to_bids
from clawneuro.skills.dicom_to_bids.runner import build_curation_request


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def _make_stub_toolchain(tmp_path: Path, *, dcm2niix_version_line: str = "dcm2niix 1.0.20250506") -> dict[str, Path]:
    tool_root = tmp_path / "toolchain"
    tool_root.mkdir()

    curation = _write_executable(
        tool_root / "dcm2bids",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import pathlib
            import shutil
            import sys

            if "--version" in sys.argv:
                print("dcm2bids 3.2.0")
                raise SystemExit(0)

            args = sys.argv[1:]
            output_root = pathlib.Path(args[args.index("-o") + 1])
            participant = args[args.index("-p") + 1]
            if shutil.which("dcm2niix") is None:
                print("dcm2niix missing", file=sys.stderr)
                raise SystemExit(1)

            func_dir = output_root / f"sub-{participant}" / "func"
            func_dir.mkdir(parents=True, exist_ok=True)
            (output_root / "dataset_description.json").write_text(
                json.dumps({"Name": "Stub Converted Dataset", "BIDSVersion": "1.10.0"}) + "\\n",
                encoding="utf-8",
            )
            (output_root / "README").write_text("stub dataset\\n", encoding="utf-8")
            (func_dir / f"sub-{participant}_task-rest_bold.nii.gz").write_text("stub-bold\\n", encoding="utf-8")
            (func_dir / f"sub-{participant}_task-rest_bold.json").write_text(
                json.dumps({"TaskName": "rest"}) + "\\n",
                encoding="utf-8",
            )
            print(json.dumps({"status": "converted"}))
            """
        ),
    )
    dcm2niix = _write_executable(
        tool_root / "dcm2niix",
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys

            if "--version" in sys.argv or "-v" in sys.argv:
                version_line = {dcm2niix_version_line!r}
                if version_line:
                    print(version_line)
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
    )
    validator = _write_executable(
        tool_root / "bids-validator-deno",
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import pathlib
            import sys

            if "--version" in sys.argv:
                print("bids-validator-deno 2.4.1")
                raise SystemExit(0)

            bids_root = pathlib.Path(sys.argv[1])
            if not (bids_root / "dataset_description.json").exists():
                print(json.dumps({"issues": {"errors": [{"code": "MISSING_DESCRIPTION", "reason": "dataset_description.json missing"}], "warnings": []}}))
                raise SystemExit(1)
            print(json.dumps({"issues": {"errors": [], "warnings": []}, "summary": {"schemaVersion": "1.10.0"}}))
            """
        ),
    )

    return {
        "dcm2bids": curation,
        "dcm2niix": dcm2niix,
        "validator": validator,
    }


def test_dicom_to_bids_dry_run_writes_conversion_manifest(tmp_path, fixtures_root):
    result = run_dicom_to_bids(
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "dicom-to-bids",
            participant_label="ID01",
            heuristic_file=fixtures_root / "dicom" / "dcm2bids_tutorial_config.json",
            execute=False,
        )
    )
    run_root = tmp_path / "dicom-to-bids"
    manifest_path = run_root / "manifests" / "conversion-manifest.json"
    assert result.status.value == "planned"
    assert (run_root / "bids_dataset").exists()
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["conversion_step"]["name"] == "dcm2bids"
    assert data["validator_step"]["name"] == "bids-validator"
    assert data["runtime_evidence"]["backend"] == "local_binary"
    assert data["conversion_step"]["command"]["argv"][:6] == [
        "dcm2bids",
        "-d",
        str(fixtures_root / "dicom" / "source"),
        "-p",
        "ID01",
        "-o",
    ]
    assert "--auto_extract_entities" in data["conversion_step"]["command"]["argv"]


def test_dicom_to_bids_execute_records_runtime_evidence_and_output_inventory(tmp_path, fixtures_root):
    toolchain = _make_stub_toolchain(tmp_path)
    result = run_dicom_to_bids(
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "dicom-to-bids-live",
            participant_label="ID01",
            heuristic_file=fixtures_root / "dicom" / "dcm2bids_tutorial_config.json",
            execute=True,
            curation_executable=str(toolchain["dcm2bids"]),
            dcm2niix_executable=str(toolchain["dcm2niix"]),
            validator_executable=str(toolchain["validator"]),
        )
    )

    manifest = json.loads(
        (tmp_path / "dicom-to-bids-live" / "manifests" / "conversion-manifest.json").read_text(encoding="utf-8")
    )

    assert result.status.value == "succeeded"
    assert result.dataset_inventory.dataset_name == "Stub Converted Dataset"
    assert result.dataset_inventory.modalities == ["bold"]
    assert manifest["runtime_evidence"]["runtime_provenance_complete"] is True
    assert all(tool["available"] for tool in manifest["runtime_evidence"]["tools"])
    assert all(tool["version_captured"] for tool in manifest["runtime_evidence"]["tools"])


def test_dicom_to_bids_execute_returns_partial_when_runtime_versions_are_missing(tmp_path, fixtures_root):
    toolchain = _make_stub_toolchain(tmp_path, dcm2niix_version_line="")
    result = run_dicom_to_bids(
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "dicom-to-bids-partial",
            participant_label="ID01",
            heuristic_file=fixtures_root / "dicom" / "dcm2bids_tutorial_config.json",
            execute=True,
            curation_executable=str(toolchain["dcm2bids"]),
            dcm2niix_executable=str(toolchain["dcm2niix"]),
            validator_executable=str(toolchain["validator"]),
        )
    )

    manifest = json.loads(
        (tmp_path / "dicom-to-bids-partial" / "manifests" / "conversion-manifest.json").read_text(encoding="utf-8")
    )

    assert result.status.value == "partial"
    assert manifest["runtime_evidence"]["runtime_provenance_complete"] is False
    assert manifest["runtime_evidence"]["versions_captured"] is False
    assert any(warning.code == "runtime-provenance-incomplete" for warning in result.warnings)


def test_build_dcm2bids_container_request_uses_stable_paths(tmp_path, fixtures_root):
    bids_root = tmp_path / "bids_dataset"
    bids_root.mkdir()

    request = build_curation_request(
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "run",
            participant_label="ID01",
            heuristic_file=fixtures_root / "dicom" / "dcm2bids_tutorial_config.json",
            backend=ExecutionBackend.DOCKER,
            conversion_image="unfmontreal/dcm2bids:3.2.0",
            validator_image="ghcr.io/bids-standard/bids-validator:v2.4.1",
        ),
        bids_root,
    )

    assert request.use_container_entrypoint is True
    assert request.args == [
        "-d",
        "/clawneuro/input",
        "-p",
        "ID01",
        "-o",
        "/clawneuro/output",
        "-c",
        "/clawneuro/config/dcm2bids_tutorial_config.json",
        "--auto_extract_entities",
    ]
    assert {str(mount.target) for mount in request.bind_mounts} == {
        "/clawneuro/input",
        "/clawneuro/output",
        "/clawneuro/config",
    }


def test_container_backend_requires_pinned_images(tmp_path, fixtures_root):
    with pytest.raises(ValidationError):
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "run",
            participant_label="ID01",
            backend=ExecutionBackend.DOCKER,
            conversion_image="unfmontreal/dcm2bids:latest",
            validator_image="ghcr.io/bids-standard/bids-validator:v2.4.1",
        )
