"""Helpers for canonical run-directory structure."""

from __future__ import annotations

from pathlib import Path

from clawneuro.core.models import ClawBaseModel


class RunDirectoryLayout(ClawBaseModel):
    """Canonical directory layout for skill outputs."""

    root: Path
    report_dir: Path
    manifests_dir: Path
    logs_dir: Path
    provenance_dir: Path
    derivatives_dir: Path


def build_run_layout(root: Path) -> RunDirectoryLayout:
    """Describe the canonical run layout without writing to disk."""

    return RunDirectoryLayout(
        root=root,
        report_dir=root / "report",
        manifests_dir=root / "manifests",
        logs_dir=root / "logs",
        provenance_dir=root / "provenance",
        derivatives_dir=root / "derivatives",
    )


def ensure_run_layout(root: Path) -> RunDirectoryLayout:
    """Create the canonical run layout."""

    layout = build_run_layout(root)
    for path in (
        layout.root,
        layout.report_dir,
        layout.manifests_dir,
        layout.logs_dir,
        layout.provenance_dir,
        layout.derivatives_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)
    return layout
