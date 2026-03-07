from __future__ import annotations

import json

import pytest

from clawneuro.core import CommandRecord, ExecutionBackend, InvalidInputStateError, RunStatus
from clawneuro.skills.bids_auditor import BidsAuditorConfig, run_bids_auditor
from clawneuro.skills.bids_auditor.runner import (
    ValidatorEvidence,
    ValidatorEvidenceMode,
    build_validator_request,
    normalize_validator_output,
)


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
    assert summary["evidence"]["mode"] == "planned"


def test_bids_auditor_rejects_dicom_input(tmp_path, fixtures_root):
    with pytest.raises(InvalidInputStateError):
        run_bids_auditor(
            BidsAuditorConfig(
                bids_root=fixtures_root / "dicom" / "source",
                output_root=tmp_path / "invalid",
            )
        )


def test_normalize_validator_output_supports_current_validator_json(fixtures_root):
    raw = json.loads(
        (fixtures_root / "fidelity" / "bids_validator" / "ds005_validator_v241_excerpt.json").read_text(
            encoding="utf-8"
        )
    )

    summary = normalize_validator_output(
        raw,
        status=RunStatus.FAILED,
        evidence=ValidatorEvidence(
            mode=ValidatorEvidenceMode.PINNED_FIDELITY_FIXTURE,
            tool_name="bids-validator-deno",
            tool_version="2.4.1",
            source_dataset="bids-examples/ds005",
            source_reference="8bb0cdd090e25180ee2f0d35b02bb45a1fb49e2b",
            fixture_path=fixtures_root / "fidelity" / "bids_validator" / "ds005_validator_v241_excerpt.json",
        ),
    )

    assert summary.warnings == 4
    assert summary.errors == 0
    assert summary.schema_version == "1.2.1"
    assert summary.evidence.mode.value == "pinned_fidelity_fixture"
    assert summary.issues[0].code == "UNKNOWN_BIDS_VERSION"


def test_bids_auditor_builds_container_request_with_stable_paths(tmp_path, fixtures_root):
    validator_config = tmp_path / "validator-config.json"
    validator_config.write_text('{"ignore": ["NO_AUTHORS"]}\n', encoding="utf-8")

    request = build_validator_request(
        BidsAuditorConfig(
            bids_root=fixtures_root / "bids" / "minimal",
            output_root=tmp_path / "audit",
            backend=ExecutionBackend.DOCKER,
            container_image="ghcr.io/bids-standard/bids-validator:v2.4.1",
            validator_config=validator_config,
        )
    )

    assert request.use_container_entrypoint is True
    assert request.args[:4] == [
        "/clawneuro/input",
        "--format",
        "json",
        "--config",
    ]
    assert request.args[4] == "/clawneuro/config/validator-config.json"
    assert {str(mount.target) for mount in request.bind_mounts} == {
        "/clawneuro/input",
        "/clawneuro/config",
    }


def test_bids_auditor_marks_unparseable_stdout(tmp_path, fixtures_root, monkeypatch):
    def fake_execute(request, stdout_path=None, stderr_path=None):
        assert stdout_path is not None
        assert stderr_path is not None
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text("not-json\n", encoding="utf-8")
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

    monkeypatch.setattr("clawneuro.skills.bids_auditor.runner.execute_request", fake_execute)
    result = run_bids_auditor(
        BidsAuditorConfig(
            bids_root=fixtures_root / "bids" / "minimal",
            output_root=tmp_path / "audit-exec",
            execute=True,
        )
    )

    assert any(warning.code == "validator-json-unparseable" for warning in result.warnings)
