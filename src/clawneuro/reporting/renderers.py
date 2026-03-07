"""Deterministic report assembly and methods rendering."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, List, Sequence

from clawneuro.core.models import ArtifactRecord, RunManifest, WarningRecord
from clawneuro.reporting.models import ReportBundleDraft, ReportSection


def aggregate_warnings(*warning_groups: Iterable[WarningRecord]) -> List[WarningRecord]:
    """Deduplicate warnings while preserving stable order."""

    unique = OrderedDict()
    for warning_group in warning_groups:
        for warning in warning_group:
            key = (warning.code, warning.severity.value, warning.message, warning.hint)
            unique[key] = warning
    return list(unique.values())


def build_artifact_index(artifacts: Sequence[ArtifactRecord]) -> dict[str, list[str]]:
    """Group artifacts by kind for report summaries."""

    grouped: dict[str, list[str]] = {}
    for artifact in artifacts:
        grouped.setdefault(artifact.kind.value, []).append(str(artifact.path))
    return {kind: sorted(paths) for kind, paths in sorted(grouped.items())}


def render_methods_text(manifest: RunManifest) -> str:
    """Render a deterministic methods paragraph from manifest metadata."""

    inventory = manifest.dataset_inventory
    tools = ", ".join(
        "{0} {1}".format(item.name, item.version or "version-unspecified")
        for item in manifest.provenance.software
    )
    if not tools:
        tools = "the recorded ClawNeuro toolchain"
    modalities = ", ".join(inventory.modalities) if inventory.modalities else "unspecified modalities"
    participants = len(inventory.subject_ids)

    return (
        "The ClawNeuro skill `{skill}` was run on dataset `{dataset}` "
        "({participants} participant(s); modalities: {modalities}). "
        "Execution metadata were assembled deterministically from the run manifest, recorded commands, "
        "and wrapped-tool version metadata. Wrapped tools for this run were {tools}. "
        "Exact commands, warnings, and reproducibility artifacts are included with the run output."
    ).format(
        skill=manifest.skill.name,
        dataset=inventory.dataset_name,
        participants=participants,
        modalities=modalities,
        tools=tools,
    )


def assemble_execution_report(manifests: Sequence[RunManifest]) -> ReportBundleDraft:
    """Combine one or more manifests into a deterministic markdown-ready bundle."""

    all_artifacts: List[ArtifactRecord] = []
    sections: List[ReportSection] = []
    warnings: List[WarningRecord] = []

    for manifest in manifests:
        methods_text = render_methods_text(manifest)
        section_artifacts = list(manifest.artifacts)
        all_artifacts.extend(section_artifacts)
        warnings.extend(manifest.warnings)
        sections.append(
            ReportSection(
                title=manifest.skill.name,
                body="\n".join(
                    [
                        manifest.result_summary,
                        "",
                        "Methods:",
                        methods_text,
                    ]
                ),
                warnings=manifest.warnings,
                artifacts=section_artifacts,
            )
        )

    return ReportBundleDraft(
        title="ClawNeuro Execution Report",
        sections=sections,
        warnings=aggregate_warnings(warnings),
        artifact_index=build_artifact_index(all_artifacts),
    )


def render_markdown_report(bundle: ReportBundleDraft) -> str:
    """Render a report bundle to markdown."""

    lines = ["# {0}".format(bundle.title), ""]
    if bundle.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(
            "- [{0}] {1}".format(warning.severity.value, warning.message) for warning in bundle.warnings
        )
        lines.append("")

    if bundle.artifact_index:
        lines.extend(["## Artifact Index", ""])
        for kind, paths in bundle.artifact_index.items():
            lines.append("- {0}: {1}".format(kind, ", ".join(paths)))
        lines.append("")

    for section in bundle.sections:
        lines.extend(["## {0}".format(section.title), "", section.body, ""])
        if section.warnings:
            lines.extend(
                "- warning: {0}".format(warning.message) for warning in section.warnings
            )
            lines.append("")

    return "\n".join(lines).strip() + "\n"
