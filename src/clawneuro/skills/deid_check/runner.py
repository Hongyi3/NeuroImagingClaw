"""Runner for the de-identification readiness skill."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic import Field

from clawneuro import __version__
from clawneuro.core import (
    ArtifactKind,
    ArtifactRecord,
    InputDatasetKind,
    InvalidInputStateError,
    RunStatus,
    SkillDescriptor,
    SkillKind,
    SkillResult,
    WarningRecord,
    WarningSeverity,
    detect_input_state,
    ensure_run_layout,
    inspect_bids_dataset,
)
from clawneuro.core.models import ClawBaseModel, ProvenanceRecord, SoftwareInventoryRecord
from clawneuro.skills.common import finalize_skill_result
from clawneuro.skills.deid_check.config import DeidCheckConfig


class ShareabilitySummary(ClawBaseModel):
    """Machine-readable shareability and privacy-readiness summary."""

    policy_profile: str
    openneuro_ready: bool
    has_structural_images: bool
    structural_privacy_status: str
    blockers: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


def _structural_files(root: Path) -> List[Path]:
    files = []
    for pattern in ("*_T1w.nii", "*_T1w.nii.gz", "*_T2w.nii", "*_T2w.nii.gz"):
        files.extend(sorted(root.rglob(pattern)))
    return sorted(files)


def _structural_privacy_status(root: Path) -> str:
    statuses = []
    for image_path in _structural_files(root):
        sidecar = image_path.with_suffix("").with_suffix(".json")
        if sidecar.exists():
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            if metadata.get("Defaced") is True or metadata.get("FaceRemoval") is True:
                statuses.append("declared_defaced")
            else:
                statuses.append("not_documented")
        else:
            statuses.append("missing_sidecar")

    if not statuses:
        return "no_structural_images"
    if all(status == "declared_defaced" for status in statuses):
        return "declared_defaced"
    if "missing_sidecar" in statuses:
        return "missing_sidecar"
    return "not_documented"


def _checklist(summary: ShareabilitySummary) -> str:
    lines = ["# Export Readiness Checklist", ""]
    lines.append("- OpenNeuro-ready: `{0}`".format(str(summary.openneuro_ready).lower()))
    lines.append("- Structural privacy status: `{0}`".format(summary.structural_privacy_status))
    lines.append("")
    lines.append("## Blockers")
    if summary.blockers:
        lines.extend("- {0}".format(item) for item in summary.blockers)
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    if summary.warnings:
        lines.extend("- {0}".format(item) for item in summary.warnings)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def run_deid_check(config: DeidCheckConfig) -> SkillResult:
    """Assess BIDS dataset shareability without making ethical or legal claims."""

    input_state = detect_input_state(config.bids_root)
    if input_state.kind not in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        raise InvalidInputStateError(
            "deid_check requires a BIDS dataset root.",
            context={"path": str(config.bids_root), "detected_kind": input_state.kind.value},
        )

    inventory = inspect_bids_dataset(config.bids_root)
    layout = ensure_run_layout(config.output_root)
    structural_status = _structural_privacy_status(config.bids_root)
    blockers: List[str] = []
    warnings: List[str] = []

    if not inventory.has_dataset_description:
        blockers.append("dataset_description.json is required before claiming BIDS or OpenNeuro readiness.")
    if inventory.dataset_readme_path is None:
        warnings.append("A dataset README is not present; sharing context may be incomplete.")
    if structural_status in {"not_documented", "missing_sidecar"}:
        blockers.append(
            "Structural images do not carry explicit defacing or face-removal metadata."
        )
    if structural_status == "no_structural_images":
        warnings.append("No structural images were detected; confirm that this matches the intended sharing scope.")

    summary = ShareabilitySummary(
        policy_profile=config.policy_profile,
        openneuro_ready=len(blockers) == 0,
        has_structural_images=structural_status != "no_structural_images",
        structural_privacy_status=structural_status,
        blockers=blockers,
        warnings=warnings,
    )
    summary_path = layout.manifests_dir / "shareability-summary.json"
    summary_path.write_text(summary.model_dump_json(indent=2) + "\n", encoding="utf-8")
    checklist_path = layout.report_dir / "export-readiness-checklist.md"
    checklist_path.write_text(_checklist(summary), encoding="utf-8")

    warning_records = [
        WarningRecord(
            code="shareability-blocker",
            severity=WarningSeverity.ERROR,
            message=item,
        )
        for item in blockers
    ]
    warning_records.extend(
        WarningRecord(
            code="shareability-warning",
            severity=WarningSeverity.WARNING,
            message=item,
        )
        for item in warnings
    )

    result = SkillResult(
        skill=SkillDescriptor(
            name="deid_check",
            kind=SkillKind.PRIVACY,
            version=__version__,
            contract_path=Path("skills/deid_check/SKILL.md"),
        ),
        status=RunStatus.SUCCEEDED,
        summary="Assessed technical export readiness with conservative structural-image privacy checks.",
        input_state=input_state,
        dataset_inventory=inventory,
        warnings=warning_records,
        artifacts=[
            ArtifactRecord(
                kind=ArtifactKind.MANIFEST,
                path=summary_path,
                description="Machine-readable shareability summary.",
                media_type="application/json",
                generated_by="deid_check",
            ),
            ArtifactRecord(
                kind=ArtifactKind.REPORT,
                path=checklist_path,
                description="Human-readable export-readiness checklist.",
                media_type="text/markdown",
                generated_by="deid_check",
            ),
        ],
        provenance=ProvenanceRecord(
            commands=[],
            software=[
                SoftwareInventoryRecord(name="clawneuro", version=__version__, role="privacy-check"),
            ],
        ),
        handoff_targets=["report_bundle"],
        benchmark_tracks=["smoke"],
    )

    finalized_result, _ = finalize_skill_result(
        layout=layout,
        result=result,
        requested_config=config,
        notes=[
            "deid_check performs technical readiness assessment only and does not certify ethics or consent.",
        ],
    )
    return finalized_result
