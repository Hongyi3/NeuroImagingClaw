from __future__ import annotations

import json

from clawneuro.skills.dicom_to_bids import DicomToBidsConfig, run_dicom_to_bids


def test_dicom_to_bids_dry_run_writes_conversion_manifest(tmp_path, fixtures_root):
    result = run_dicom_to_bids(
        DicomToBidsConfig(
            source_root=fixtures_root / "dicom" / "source",
            output_root=tmp_path / "dicom-to-bids",
            execute=False,
        )
    )
    run_root = tmp_path / "dicom-to-bids"
    manifest_path = run_root / "manifests" / "conversion-manifest.json"
    assert result.status.value == "planned"
    assert (run_root / "bids_dataset").exists()
    assert manifest_path.exists()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(data["planned_steps"]) == 3
    assert data["planned_steps"][-1]["name"] == "bids-validator"
