from __future__ import annotations

import json
import shutil

import pytest

from clawneuro.core import InvalidInputStateError
from clawneuro.skills.deid_check import DeidCheckConfig, run_deid_check


def test_deid_check_flags_missing_defacing_metadata(tmp_path, fixtures_root):
    run_deid_check(
        DeidCheckConfig(
            bids_root=fixtures_root / "bids" / "minimal",
            output_root=tmp_path / "deid-minimal",
        )
    )
    summary = json.loads(
        (tmp_path / "deid-minimal" / "manifests" / "shareability-summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["openneuro_ready"] is False
    assert summary["structural_privacy_status"] == "not_documented"
    assert any(rule["rule_id"] == "DP003" and rule["passed"] is False for rule in summary["rule_results"])


def test_deid_check_accepts_declared_defaced_structural_images(tmp_path, fixtures_root):
    result = run_deid_check(
        DeidCheckConfig(
            bids_root=fixtures_root / "bids" / "defaced",
            output_root=tmp_path / "deid-defaced",
        )
    )
    summary = json.loads(
        (tmp_path / "deid-defaced" / "manifests" / "shareability-summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert result.status.value == "succeeded"
    assert summary["openneuro_ready"] is True
    assert summary["structural_privacy_status"] == "declared_defaced"
    assert any(rule["rule_id"] == "DP003" and rule["passed"] is True for rule in summary["rule_results"])


def test_deid_check_warns_when_readme_missing(tmp_path, fixtures_root):
    dataset_root = tmp_path / "bids-no-readme"
    shutil.copytree(fixtures_root / "bids" / "defaced", dataset_root)
    (dataset_root / "README").unlink()

    run_deid_check(
        DeidCheckConfig(
            bids_root=dataset_root,
            output_root=tmp_path / "deid-no-readme",
        )
    )
    summary = json.loads(
        (tmp_path / "deid-no-readme" / "manifests" / "shareability-summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["openneuro_ready"] is True
    assert any(rule["rule_id"] == "DP002" and rule["passed"] is False for rule in summary["rule_results"])


def test_deid_check_handles_no_structural_images(tmp_path):
    dataset_root = tmp_path / "bids-no-structural"
    dataset_root.mkdir()
    (dataset_root / "dataset_description.json").write_text(
        '{"Name": "No Structural", "BIDSVersion": "1.10.0", "DatasetType": "raw"}\n',
        encoding="utf-8",
    )
    (dataset_root / "README").write_text("No structural images in this fixture.\n", encoding="utf-8")

    run_deid_check(
        DeidCheckConfig(
            bids_root=dataset_root,
            output_root=tmp_path / "deid-no-structural",
        )
    )
    summary = json.loads(
        (tmp_path / "deid-no-structural" / "manifests" / "shareability-summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["openneuro_ready"] is True
    assert summary["has_structural_images"] is False
    assert summary["structural_privacy_status"] == "no_structural_images"


def test_deid_check_flags_missing_sidecar(tmp_path, fixtures_root):
    dataset_root = tmp_path / "bids-missing-sidecar"
    shutil.copytree(fixtures_root / "bids" / "defaced", dataset_root)
    (dataset_root / "sub-01" / "anat" / "sub-01_T1w.json").unlink()

    run_deid_check(
        DeidCheckConfig(
            bids_root=dataset_root,
            output_root=tmp_path / "deid-missing-sidecar",
        )
    )
    summary = json.loads(
        (tmp_path / "deid-missing-sidecar" / "manifests" / "shareability-summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["openneuro_ready"] is False
    assert summary["structural_privacy_status"] == "missing_sidecar"


def test_deid_check_rejects_non_bids_input(tmp_path, fixtures_root):
    with pytest.raises(InvalidInputStateError):
        run_deid_check(
            DeidCheckConfig(
                bids_root=fixtures_root / "dicom" / "source",
                output_root=tmp_path / "deid-invalid",
            )
        )
