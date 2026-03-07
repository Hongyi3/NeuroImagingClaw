"""Helpers for harvesting upstream QC, preprocessing, and boilerplate artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from pydantic import Field

from clawneuro.core.models import ArtifactKind, ArtifactRecord, ClawBaseModel


class HarvestedOutputs(ClawBaseModel):
    """Structured view of harvested upstream outputs."""

    root: Path
    report_paths: List[Path] = Field(default_factory=list)
    iqm_table_paths: List[Path] = Field(default_factory=list)
    confounds_paths: List[Path] = Field(default_factory=list)
    boilerplate_paths: List[Path] = Field(default_factory=list)
    dataset_description_path: Optional[Path] = None


def _stable_paths(paths: Iterable[Path]) -> List[Path]:
    return sorted({path for path in paths if path.exists() and path.is_file()})


def _media_type(path: Path) -> Optional[str]:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "text/html"
    if suffix == ".md":
        return "text/markdown"
    if suffix == ".bib":
        return "text/plain"
    if suffix == ".json":
        return "application/json"
    if suffix == ".tsv":
        return "text/tab-separated-values"
    if suffix == ".csv":
        return "text/csv"
    if suffix == ".tex":
        return "application/x-tex"
    return None


def harvest_mriqc_outputs(root: Path) -> HarvestedOutputs:
    """Collect MRIQC derivative reports and IQM tables from a derivative root."""

    report_paths = _stable_paths(root.rglob("*.html"))
    iqm_table_paths = _stable_paths(
        list(root.rglob("*.tsv")) + list(root.rglob("*.csv"))
    )
    dataset_description = root / "dataset_description.json"
    return HarvestedOutputs(
        root=root,
        report_paths=report_paths,
        iqm_table_paths=iqm_table_paths,
        dataset_description_path=dataset_description if dataset_description.exists() else None,
    )


def harvest_fmriprep_outputs(root: Path) -> HarvestedOutputs:
    """Collect fMRIPrep derivative reports, confounds, and citation boilerplate."""

    report_paths = _stable_paths(root.rglob("*.html"))
    confounds_paths = _stable_paths(
        list(root.rglob("*desc-confounds_timeseries.tsv"))
        + list(root.rglob("*desc-confounds_timeseries.json"))
    )
    logs_root = root / "logs"
    boilerplate_paths = _stable_paths(
        list(logs_root.glob("CITATION*")) + list(logs_root.glob("*boilerplate*"))
    )
    dataset_description = root / "dataset_description.json"
    return HarvestedOutputs(
        root=root,
        report_paths=report_paths,
        confounds_paths=confounds_paths,
        boilerplate_paths=boilerplate_paths,
        dataset_description_path=dataset_description if dataset_description.exists() else None,
    )


def harvested_output_artifacts(harvest: HarvestedOutputs, *, generated_by: str) -> List[ArtifactRecord]:
    """Convert harvested outputs into plain manifest artifact records."""

    artifacts: List[ArtifactRecord] = [
        ArtifactRecord(
            kind=ArtifactKind.DERIVATIVE,
            path=harvest.root,
            description="Derivative output root preserved from the wrapped upstream tool.",
            generated_by=generated_by,
        )
    ]
    if harvest.dataset_description_path is not None:
        artifacts.append(
            ArtifactRecord(
                kind=ArtifactKind.METADATA,
                path=harvest.dataset_description_path,
                description="Derivative dataset description emitted by the wrapped tool.",
                media_type="application/json",
                generated_by=generated_by,
            )
        )
    for path in harvest.report_paths:
        artifacts.append(
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=path,
                description="Preserved upstream HTML report.",
                media_type=_media_type(path),
                generated_by=generated_by,
            )
        )
    for path in harvest.iqm_table_paths:
        artifacts.append(
            ArtifactRecord(
                kind=ArtifactKind.TABLE,
                path=path,
                description="Preserved upstream IQM summary table.",
                media_type=_media_type(path),
                generated_by=generated_by,
            )
        )
    for path in harvest.confounds_paths:
        artifacts.append(
            ArtifactRecord(
                kind=ArtifactKind.TABLE if path.suffix.lower() == ".tsv" else ArtifactKind.METADATA,
                path=path,
                description="Preserved confounds output from preprocessing.",
                media_type=_media_type(path),
                generated_by=generated_by,
            )
        )
    for path in harvest.boilerplate_paths:
        artifacts.append(
            ArtifactRecord(
                kind=ArtifactKind.METADATA,
                path=path,
                description="Preserved methods and citation boilerplate from the wrapped tool.",
                media_type=_media_type(path),
                generated_by=generated_by,
            )
        )
    return artifacts
