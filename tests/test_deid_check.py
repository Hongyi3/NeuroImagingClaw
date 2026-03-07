from __future__ import annotations

import json

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
