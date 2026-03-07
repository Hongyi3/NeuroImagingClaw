from __future__ import annotations

import json

import pytest

from clawneuro.core import InvalidInputStateError
from clawneuro.skills.bids_auditor import BidsAuditorConfig, run_bids_auditor


def test_bids_auditor_dry_run_writes_contract_outputs(tmp_path, fixtures_root):
    result = run_bids_auditor(
        BidsAuditorConfig(
            bids_root=fixtures_root / "bids" / "minimal",
            output_root=tmp_path / "bids-audit",
            execute=False,
        )
    )
    run_root = tmp_path / "bids-audit"
    assert result.status.value == "planned"
    assert (run_root / "manifests" / "validator-summary.json").exists()
    assert (run_root / "report" / "audit-report.md").exists()
    assert (run_root / "report" / "triage-checklist.md").exists()
    assert (run_root / "manifests" / "run-manifest.json").exists()
    assert (run_root / "provenance" / "commands.sh").exists()
    assert (run_root / "provenance" / "checksums.sha256").exists()

    summary = json.loads((run_root / "manifests" / "validator-summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "planned"


def test_bids_auditor_rejects_dicom_input(tmp_path, fixtures_root):
    with pytest.raises(InvalidInputStateError):
        run_bids_auditor(
            BidsAuditorConfig(
                bids_root=fixtures_root / "dicom" / "source",
                output_root=tmp_path / "invalid",
            )
        )
