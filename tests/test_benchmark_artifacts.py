from __future__ import annotations

import importlib.util
import json

import pytest

from benchmarks.phase2_common import (
    PHASE2_DATASET_DOI,
    PHASE2_DATASET_SOURCE_COMMIT,
    PHASE2_PARTICIPANT_LABEL,
    PHASE2_REQUIRED_INPUTS,
    PHASE2_SESSION_ID,
    benchmark_header,
    copy_preserved_derivative_files,
    copy_run_support_dirs,
    inspect_phase2_dataset_root,
    runtime_tool_index,
    write_benchmark_metadata,
)


def test_phase1_public_dicom_benchmark_artifacts_are_checked_in(repo_root):
    artifact_root = repo_root / "benchmarks" / "artifacts" / "phase1_dcm_qa_nih"
    metadata = json.loads((artifact_root / "benchmark-metadata.json").read_text(encoding="utf-8"))
    conversion_manifest = json.loads(
        (artifact_root / "manifests" / "conversion-manifest.json").read_text(encoding="utf-8")
    )
    run_manifest = json.loads((artifact_root / "manifests" / "run-manifest.json").read_text(encoding="utf-8"))
    commands = (artifact_root / "provenance" / "commands.sh").read_text(encoding="utf-8")

    assert metadata["benchmark_id"] == "phase1_dcm_qa_nih"
    assert metadata["run"]["status"] == "succeeded"
    assert len(metadata["dataset"]["archive_sha256"]) == 64
    assert metadata["toolchain"]["runtime_tools"]["dcm2bids"]["version"]
    assert metadata["toolchain"]["runtime_tools"]["dcm2niix"]["version"]
    assert metadata["toolchain"]["runtime_tools"]["bids-validator-deno"]["version"]

    assert conversion_manifest["status"] == "succeeded"
    assert conversion_manifest["runtime_evidence"]["runtime_provenance_complete"] is True
    assert conversion_manifest["runtime_evidence"]["versions_captured"] is True
    assert run_manifest["status"] == "succeeded"
    assert run_manifest["dataset_inventory"]["modalities"] == ["bold", "fmap"]

    assert "dcm2bids" in commands
    assert "bids-validator-deno" in commands


def test_phase2_common_helpers_copy_artifacts_and_write_metadata(tmp_path):
    run_root = tmp_path / "run-output"
    for name in ("manifests", "logs", "provenance", "report"):
        directory = run_root / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")

    derivative_root = run_root / "derivatives"
    (derivative_root / "reports").mkdir(parents=True, exist_ok=True)
    report_path = derivative_root / "reports" / "sub-01_T1w.html"
    report_path.write_text("<html></html>\n", encoding="utf-8")

    artifact_root = tmp_path / "artifacts"
    copy_run_support_dirs(run_root, artifact_root)
    copied = copy_preserved_derivative_files(derivative_root, artifact_root, [report_path])

    metadata = benchmark_header("phase2_ds003020_mriqc")
    metadata["toolchain"] = {
        "runtime_tools": runtime_tool_index(
            {
                "provenance": {
                    "software": [
                        {"name": "docker", "version": "Docker version 26.1.0", "role": "container-runtime"},
                        {
                            "name": "mriqc",
                            "container_image": "nipreps/mriqc:24.0.0",
                            "container_digest": "sha256:test",
                        },
                    ]
                }
            }
        )
    }
    metadata["artifacts"] = {"preserved_outputs": copied}
    metadata_path = write_benchmark_metadata(artifact_root, metadata)
    parsed = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert (artifact_root / "manifests" / "manifests.txt").exists()
    assert copied == {"reports/sub-01_T1w.html": "preserved-derivatives/reports/sub-01_T1w.html"}
    assert parsed["benchmark_id"] == "phase2_ds003020_mriqc"
    assert parsed["toolchain"]["runtime_tools"]["docker"]["role"] == "container-runtime"
    assert parsed["toolchain"]["runtime_tools"]["mriqc"]["container_digest"] == "sha256:test"


def test_phase2_dataset_root_validation_requires_pinned_subset(tmp_path):
    dataset_root = tmp_path / "ds003020"
    dataset_root.mkdir(parents=True, exist_ok=True)
    (dataset_root / "dataset_description.json").write_text(
        json.dumps({"Name": "Pinned ds003020 subset", "DatasetDOI": PHASE2_DATASET_DOI}) + "\n",
        encoding="utf-8",
    )
    (dataset_root / "participants.tsv").write_text(
        "participant_id\tage\tsex\nsub-UTS01\t24\tF\n",
        encoding="utf-8",
    )
    for relative in PHASE2_REQUIRED_INPUTS:
        destination = dataset_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("stub\n", encoding="utf-8")

    metadata = inspect_phase2_dataset_root(dataset_root)

    assert metadata["participant_label"] == PHASE2_PARTICIPANT_LABEL
    assert metadata["session_id"] == PHASE2_SESSION_ID
    assert metadata["source_commit"] == PHASE2_DATASET_SOURCE_COMMIT
    assert metadata["selected_inputs"] == [str(path) for path in PHASE2_REQUIRED_INPUTS]


def test_phase2_dataset_root_validation_rejects_unpinned_dataset(tmp_path):
    dataset_root = tmp_path / "ds003020"
    dataset_root.mkdir(parents=True, exist_ok=True)
    (dataset_root / "dataset_description.json").write_text(
        json.dumps({"Name": "Wrong ds003020 subset", "DatasetDOI": "doi:10.18112/openneuro.ds003020.v0.0.1"}) + "\n",
        encoding="utf-8",
    )
    (dataset_root / "participants.tsv").write_text(
        "participant_id\tage\tsex\nsub-UTS01\t24\tF\n",
        encoding="utf-8",
    )
    for relative in PHASE2_REQUIRED_INPUTS:
        destination = dataset_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("stub\n", encoding="utf-8")

    with pytest.raises(ValueError, match="pinned ds003020 DOI"):
        inspect_phase2_dataset_root(dataset_root)


def test_phase2_benchmark_note_documents_ds003020_path(repo_root):
    note = (repo_root / "benchmarks" / "PHASE2_QC_PREP.md").read_text(encoding="utf-8")

    assert "ds003020" in note
    assert "UTS01" in note
    assert "ses-1" in note
    assert PHASE2_DATASET_DOI in note
    assert "run_phase2_public_mriqc.py" in note
    assert "run_phase2_public_anat_bold_prep.py" in note


def test_phase2_mriqc_benchmark_requests_bold_only_contract(repo_root, tmp_path):
    module_path = repo_root / "benchmarks" / "run_phase2_public_mriqc.py"
    spec = importlib.util.spec_from_file_location("phase2_public_mriqc", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dataset_root = tmp_path / "dataset"
    dataset_root.mkdir()

    config = module.build_phase2_mriqc_config(
        dataset_root=dataset_root,
        output_root=tmp_path / "output",
        backend=module.ExecutionBackend.DOCKER,
        container_image="nipreps/mriqc:24.0.0",
    )

    assert config.participant_labels == [PHASE2_PARTICIPANT_LABEL]
    assert config.session_ids == [PHASE2_SESSION_ID]
    assert config.modalities == ["bold"]
    assert config.run_group is True
