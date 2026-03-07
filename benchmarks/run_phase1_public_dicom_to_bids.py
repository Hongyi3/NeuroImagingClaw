#!/usr/bin/env python3
"""Run the pinned public DICOM-to-BIDS benchmark for M3 evidence."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from clawneuro import __version__
from clawneuro.provenance import sha256_file
from clawneuro.skills.dicom_to_bids import DicomToBidsConfig, run_dicom_to_bids

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_COMMIT = "d302d6e241dda747b79ee1724ada3200179755a2"
DATASET_ARCHIVE_URL = (
    "https://codeload.github.com/neurolabusc/dcm_qa_nih/tar.gz/" + DATASET_COMMIT
)
CONFIG_SOURCE = REPO_ROOT / "tests" / "fixtures" / "dicom" / "dcm2bids_tutorial_config.json"


@contextlib.contextmanager
def pushd(path: Path):
    """Temporarily change the working directory."""

    previous = Path.cwd()
    try:
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        yield
    finally:
        os.chdir(previous)


def _download_archive(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    except Exception:
        curl = shutil.which("curl")
        if not curl:
            raise
        subprocess.run(
            [curl, "-L", "--fail", url, "-o", str(destination)],
            check=True,
        )
    return destination


def _extract_archive(archive_path: Path, destination: Path) -> Path:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("Expected exactly one extracted archive root.")
    return roots[0]


def _copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True, help="Temporary benchmark workspace.")
    parser.add_argument(
        "--artifact-root",
        type=Path,
        required=True,
        help="Repository path where stable benchmark evidence will be copied.",
    )
    parser.add_argument(
        "--dataset-archive-url",
        default=DATASET_ARCHIVE_URL,
        help="Pinned archive URL for the public DICOM benchmark dataset.",
    )
    parser.add_argument(
        "--dataset-commit",
        default=DATASET_COMMIT,
        help="Pinned source commit for the public DICOM benchmark dataset.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    artifact_root = (
        args.artifact_root
        if args.artifact_root.is_absolute()
        else (REPO_ROOT / args.artifact_root).resolve()
    )

    download_dir = workspace / "downloads"
    source_dir = workspace / "sources"
    code_dir = workspace / "code"
    output_root = workspace / "run-output"
    archive_path = download_dir / ("dcm_qa_nih-" + args.dataset_commit + ".tar.gz")
    config_path = code_dir / "dcm2bids_config.json"

    if archive_path.exists():
        archive_sha256 = sha256_file(archive_path)
    else:
        _download_archive(args.dataset_archive_url, archive_path)
        archive_sha256 = sha256_file(archive_path)

    extracted_root = _extract_archive(archive_path, source_dir)
    source_root = extracted_root / "In"
    code_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CONFIG_SOURCE, config_path)
    if output_root.exists():
        shutil.rmtree(output_root)

    with pushd(workspace):
        source_root_rel = source_root.relative_to(workspace)
        config_path_rel = config_path.relative_to(workspace)
        output_root_rel = output_root.relative_to(workspace)
        tool_root = Path(sys.executable).parent
        result = run_dicom_to_bids(
            DicomToBidsConfig(
                source_root=source_root_rel,
                output_root=output_root_rel,
                participant_label="ID01",
                heuristic_file=config_path_rel,
                execute=True,
                curation_executable=str(tool_root / "dcm2bids"),
                dcm2niix_executable=str(tool_root / "dcm2niix"),
                validator_executable=str(tool_root / "bids-validator-deno"),
            )
        )

    if result.status.value != "succeeded":
        raise RuntimeError(
            "Public benchmark run did not complete successfully.",
        )

    artifact_root.mkdir(parents=True, exist_ok=True)
    for directory_name in ("manifests", "provenance", "report", "logs"):
        _copy_tree(output_root / directory_name, artifact_root / directory_name)

    run_manifest_path = artifact_root / "manifests" / "run-manifest.json"
    conversion_manifest_path = artifact_root / "manifests" / "conversion-manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    conversion_manifest = json.loads(conversion_manifest_path.read_text(encoding="utf-8"))
    runtime_tools = {
        tool["tool_name"]: {
            "requested_executable": tool["requested_executable"],
            "resolved_executable": tool.get("resolved_executable"),
            "version": tool.get("version"),
        }
        for tool in conversion_manifest["runtime_evidence"]["tools"]
    }

    benchmark_metadata = {
        "benchmark_id": "phase1_dcm_qa_nih",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clawneuro_version": __version__,
        "dataset": {
            "source_repo": "neurolabusc/dcm_qa_nih",
            "source_commit": args.dataset_commit,
            "archive_url": args.dataset_archive_url,
            "archive_sha256": archive_sha256,
            "workspace_relative_source_root": str(source_root.relative_to(workspace)),
        },
        "toolchain": {
            "python_version": sys.version.split()[0],
            "runtime_tools": runtime_tools,
        },
        "run": {
            "status": result.status.value,
            "summary": result.summary,
            "workspace_relative_output_root": str(output_root.relative_to(workspace)),
            "verification_command": "python benchmarks/run_phase1_public_dicom_to_bids.py --workspace <workspace> --artifact-root benchmarks/artifacts/phase1_dcm_qa_nih",
        },
        "artifacts": {
            "run_manifest": "manifests/run-manifest.json",
            "conversion_manifest": "manifests/conversion-manifest.json",
            "report": "report/conversion-report.md",
            "provenance": "provenance/commands.sh",
        },
        "notes": [
            "Copied artifacts preserve workspace-relative paths from the controlled benchmark run.",
            "The raw public dataset is downloaded at benchmark time and is not vendored into the repository.",
        ],
        "run_manifest_status": run_manifest["status"],
    }
    metadata_path = artifact_root / "benchmark-metadata.json"
    metadata_path.write_text(json.dumps(benchmark_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact_root": str(artifact_root), "status": result.status.value}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
