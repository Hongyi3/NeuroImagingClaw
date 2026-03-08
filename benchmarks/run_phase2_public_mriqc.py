#!/usr/bin/env python3
"""Run the pinned public MRIQC benchmark for Phase 2 evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from phase2_common import (  # noqa: E402
    PHASE2_SESSION_ID,
    PHASE2_PARTICIPANT_LABEL,
    MRIQC_DOCKER_IMAGE,
    backend_container_image,
    benchmark_header,
    copy_preserved_derivative_files,
    copy_run_support_dirs,
    inspect_phase2_dataset_root,
    runtime_tool_index,
    verification_command,
    write_benchmark_metadata,
)

from clawneuro import __version__  # noqa: E402
from clawneuro.core import ExecutionBackend  # noqa: E402
from clawneuro.reporting import harvest_mriqc_outputs  # noqa: E402
from clawneuro.skills.mriqc_report import MRIQCReportConfig, run_mriqc_report  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True, help="Local public BIDS root for ds003020.")
    parser.add_argument("--workspace", type=Path, required=True, help="Temporary benchmark workspace.")
    parser.add_argument(
        "--artifact-root",
        type=Path,
        required=True,
        help="Repository path where stable benchmark evidence should be copied.",
    )
    parser.add_argument(
        "--backend",
        choices=("docker", "apptainer"),
        default="docker",
        help="Container backend used for the live benchmark run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.resolve()
    dataset_root = args.dataset_root.resolve()
    artifact_root = args.artifact_root if args.artifact_root.is_absolute() else (SCRIPT_ROOT.parent / args.artifact_root)
    artifact_root = artifact_root.resolve()
    dataset_metadata = inspect_phase2_dataset_root(dataset_root)

    output_root = workspace / "run-output"
    container_image = backend_container_image(args.backend, MRIQC_DOCKER_IMAGE)
    backend = ExecutionBackend(args.backend)
    result = run_mriqc_report(
        MRIQCReportConfig(
            bids_root=dataset_root,
            output_root=output_root,
            execute=True,
            backend=backend,
            container_image=container_image,
            participant_labels=[PHASE2_PARTICIPANT_LABEL],
            session_ids=[PHASE2_SESSION_ID],
            modalities=["anat", "bold"],
            run_group=True,
            nprocs=2,
            omp_nthreads=2,
            mem_gb=12,
        )
    )
    if result.status.value != "succeeded":
        failure_payload = {
            "status": result.status.value,
            "summary": result.summary,
            "warnings": [warning.model_dump(mode="json") for warning in result.warnings],
            "artifacts": [artifact.model_dump(mode="json") for artifact in result.artifacts],
        }
        summary_path = output_root / "manifests" / "mriqc-summary.json"
        if summary_path.exists():
            failure_payload["summary_manifest"] = json.loads(summary_path.read_text(encoding="utf-8"))
        run_manifest_path = output_root / "manifests" / "run-manifest.json"
        if run_manifest_path.exists():
            failure_payload["run_manifest"] = json.loads(run_manifest_path.read_text(encoding="utf-8"))
        print(json.dumps(failure_payload, indent=2))
        raise RuntimeError("Phase 2 MRIQC benchmark did not complete successfully.")

    copy_run_support_dirs(output_root, artifact_root)
    harvest = harvest_mriqc_outputs(output_root / "derivatives")
    preserved_outputs = copy_preserved_derivative_files(
        output_root / "derivatives",
        artifact_root,
        list(harvest.report_paths) + list(harvest.iqm_table_paths) + ([harvest.dataset_description_path] if harvest.dataset_description_path else []),
    )

    run_manifest = json.loads((artifact_root / "manifests" / "run-manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((artifact_root / "manifests" / "mriqc-summary.json").read_text(encoding="utf-8"))

    metadata = benchmark_header("phase2_ds003020_mriqc")
    metadata.update(
        {
            "clawneuro_version": __version__,
            "dataset": dataset_metadata,
            "toolchain": {
                "python_version": sys.version.split()[0],
                "backend": args.backend,
                "container_image": container_image,
                "runtime_tools": runtime_tool_index(run_manifest),
            },
            "run": {
                "status": result.status.value,
                "summary": result.summary,
                "requested_resources": {"nprocs": 2, "omp_nthreads": 2, "mem_gb": 12},
                "workspace_relative_output_root": str(output_root.relative_to(workspace)),
                "verification_command": verification_command(
                    Path(__file__).name,
                    dataset_root=str(dataset_root),
                    workspace=str(workspace),
                    artifact_root=str(artifact_root),
                    backend=args.backend,
                ),
            },
            "artifacts": {
                "run_manifest": "manifests/run-manifest.json",
                "summary_manifest": "manifests/mriqc-summary.json",
                "report": "report/mriqc-report.md",
                "provenance": "provenance/commands.sh",
                "preserved_outputs": preserved_outputs,
            },
            "summary_status": summary["status"],
            "notes": [
                "This benchmark proves one live ds003020 MRIQC path executed on the pinned sub-UTS01/ses-1 subset with container provenance and preserved QC outputs.",
                "It does not prove downstream modeling, resting-state connectivity, multi-dataset generality, or scientific superiority over upstream tools.",
                "Copied artifact files preserve selected derivative evidence only; the raw public dataset is not vendored into the repository.",
            ],
        }
    )
    write_benchmark_metadata(artifact_root, metadata)
    print(json.dumps({"artifact_root": str(artifact_root), "status": result.status.value}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
