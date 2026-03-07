"""Typer application entrypoints for ClawNeuro."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from clawneuro.core import RunManifest, ensure_run_layout, load_config
from clawneuro.orchestrator import plan_phase1_workflow
from clawneuro.provenance import write_provenance_bundle, write_run_manifest
from clawneuro.reporting import assemble_execution_report, render_markdown_report
from clawneuro.skills import (
    BidsAuditorConfig,
    DeidCheckConfig,
    DicomToBidsConfig,
    run_bids_auditor,
    run_deid_check,
    run_dicom_to_bids,
)

app = typer.Typer(help="ClawNeuro CLI for planning, intake, audit, and provenance tasks.")


def _manifest_json_from_result(result, requested_config):
    manifest = RunManifest.from_result(result, requested_config=requested_config.model_dump(mode="json"))
    return manifest.model_dump_json(indent=2)


@app.command("plan")
def plan_command(
    input_path: Path = typer.Argument(..., help="Input path to inspect."),
    goal: str = typer.Option("phase1-foundation", help="Planning goal label."),
) -> None:
    """Plan the appropriate Phase 1 workflow for an input path."""

    plan = plan_phase1_workflow(input_path, goal=goal)
    typer.echo(plan.model_dump_json(indent=2))


@app.command("bids-auditor")
def bids_auditor_command(
    bids_root: Path = typer.Option(..., help="BIDS dataset root."),
    output_root: Path = typer.Option(..., help="Output directory for run artifacts."),
    config_path: Optional[Path] = typer.Option(None, help="Optional config file."),
    execute: bool = typer.Option(False, help="Execute wrapped validator if installed."),
) -> None:
    """Plan or run the BIDS auditor skill."""

    config = load_config(config_path, BidsAuditorConfig) if config_path else BidsAuditorConfig(
        bids_root=bids_root,
        output_root=output_root,
        execute=execute,
    )
    if config_path:
        config = config.model_copy(update={"execute": execute})
    result = run_bids_auditor(config)
    typer.echo(_manifest_json_from_result(result, config))


@app.command("dicom-to-bids")
def dicom_to_bids_command(
    source_root: Path = typer.Option(..., help="DICOM-like source directory."),
    output_root: Path = typer.Option(..., help="Output directory for run artifacts."),
    config_path: Optional[Path] = typer.Option(None, help="Optional config file."),
    execute: bool = typer.Option(False, help="Execute wrapped conversion tools if installed."),
) -> None:
    """Plan or run DICOM-to-BIDS conversion."""

    config = load_config(config_path, DicomToBidsConfig) if config_path else DicomToBidsConfig(
        source_root=source_root,
        output_root=output_root,
        execute=execute,
    )
    if config_path:
        config = config.model_copy(update={"execute": execute})
    result = run_dicom_to_bids(config)
    typer.echo(_manifest_json_from_result(result, config))


@app.command("deid-check")
def deid_check_command(
    bids_root: Path = typer.Option(..., help="BIDS dataset root."),
    output_root: Path = typer.Option(..., help="Output directory for run artifacts."),
    config_path: Optional[Path] = typer.Option(None, help="Optional config file."),
) -> None:
    """Run the local privacy-readiness assessment."""

    config = load_config(config_path, DeidCheckConfig) if config_path else DeidCheckConfig(
        bids_root=bids_root,
        output_root=output_root,
    )
    result = run_deid_check(config)
    typer.echo(_manifest_json_from_result(result, config))


@app.command("report-bundle")
def report_bundle_command(
    manifest_paths: List[Path] = typer.Argument(..., help="One or more run manifest JSON files."),
    output_path: Path = typer.Option(..., help="Markdown path for the assembled report bundle."),
) -> None:
    """Assemble a deterministic markdown report from one or more run manifests."""

    manifests = [
        RunManifest.model_validate_json(path.read_text(encoding="utf-8"))
        for path in manifest_paths
    ]
    bundle = assemble_execution_report(manifests)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(bundle), encoding="utf-8")
    typer.echo(str(output_path))


@app.command("repro-bundle")
def repro_bundle_command(
    manifest_path: Path = typer.Option(..., help="Existing run manifest JSON."),
    output_root: Path = typer.Option(..., help="Output directory for the reproduced provenance bundle."),
    artifact_paths: Optional[List[Path]] = typer.Option(
        None,
        help="Additional artifact paths to checksum.",
    ),
) -> None:
    """Write the minimum reproducibility bundle for an existing manifest."""

    manifest = RunManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    layout = ensure_run_layout(output_root)
    provenance = write_provenance_bundle(
        layout=layout,
        manifest=manifest,
        artifact_paths=artifact_paths,
        notes=["Repro bundle created from an existing run manifest via the CLI."],
    )
    manifest = manifest.model_copy(update={"provenance": provenance})
    write_run_manifest(layout.manifests_dir / "run-manifest.json", manifest)
    typer.echo(json.dumps({"output_root": str(output_root), "status": "written"}, indent=2))


def main() -> None:
    """CLI entrypoint for console scripts and python -m usage."""

    app()
