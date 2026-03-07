"""Planning-only types for orchestration decisions."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field

from clawneuro.core.bids import detect_input_state, inspect_bids_dataset
from clawneuro.core.models import (
    ClawBaseModel,
    DatasetInventory,
    InputDatasetKind,
    RunStatus,
    SkillInputState,
    WarningRecord,
    WarningSeverity,
)


class DatasetInspection(ClawBaseModel):
    """Normalized inspection result used by the planner."""

    path: Path
    input_state: SkillInputState
    dataset_inventory: Optional[DatasetInventory] = None
    recommended_skills: List[str] = Field(default_factory=list)
    blockers: List[WarningRecord] = Field(default_factory=list)


class PlannedSkillRun(ClawBaseModel):
    """Single planned skill execution."""

    skill_name: str
    rationale: str
    requires: List[str] = Field(default_factory=list)
    produces: List[str] = Field(default_factory=list)
    status: RunStatus = RunStatus.PLANNED


class SkillHandoff(ClawBaseModel):
    """Explicit handoff between two skills."""

    from_skill: str
    to_skill: str
    required_artifacts: List[str] = Field(default_factory=list)
    rationale: str


class OrchestrationPlan(ClawBaseModel):
    """Cross-skill execution plan without scientific execution logic."""

    goal: str
    input_path: Path
    inspection: DatasetInspection
    steps: List[PlannedSkillRun] = Field(default_factory=list)
    handoffs: List[SkillHandoff] = Field(default_factory=list)
    warnings: List[WarningRecord] = Field(default_factory=list)


def inspect_dataset(path: Path) -> DatasetInspection:
    """Inspect a repository path and recommend the next skills."""

    input_state = detect_input_state(path)
    warnings: List[WarningRecord] = []
    inventory = None
    recommended_skills: List[str] = []

    if not input_state.readable:
        warnings.append(
            WarningRecord(
                code="input-unreadable",
                severity=WarningSeverity.ERROR,
                message="Input path is not readable.",
                hint="Check the path and permissions before running a skill.",
            )
        )
    elif input_state.kind in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        inventory = inspect_bids_dataset(path)
        recommended_skills.extend(["bids_auditor", "deid_check"])
        if "bold" in inventory.modalities or "anat" in inventory.modalities:
            recommended_skills.extend(["mriqc_report", "anat_bold_prep"])
        if "dwi" in inventory.modalities:
            recommended_skills.append("diffusion_prep")
        if not inventory.has_dataset_description:
            warnings.append(
                WarningRecord(
                    code="missing-dataset-description",
                    severity=WarningSeverity.ERROR,
                    message="dataset_description.json is required for BIDS-compliant workflows.",
                    hint="Add dataset_description.json before treating the dataset as BIDS-complete.",
                )
            )
    elif input_state.kind == InputDatasetKind.DICOM:
        recommended_skills.extend(["dicom_to_bids", "bids_auditor", "deid_check"])
    else:
        warnings.append(
            WarningRecord(
                code="unknown-input-kind",
                severity=WarningSeverity.ERROR,
                message="Input path does not match a supported workflow state.",
                hint="Provide a DICOM directory or a BIDS dataset root.",
            )
        )

    return DatasetInspection(
        path=path,
        input_state=input_state,
        dataset_inventory=inventory,
        recommended_skills=recommended_skills,
        blockers=warnings,
    )


def plan_phase1_workflow(path: Path, goal: str = "phase1-intake-audit") -> OrchestrationPlan:
    """Create an explicit Phase 1 skill plan for a given input path."""

    inspection = inspect_dataset(path)
    steps: List[PlannedSkillRun] = []
    handoffs: List[SkillHandoff] = []

    if inspection.input_state.kind == InputDatasetKind.DICOM:
        steps.append(
            PlannedSkillRun(
                skill_name="dicom_to_bids",
                rationale="DICOM-like inputs must be curated into BIDS before downstream audit or privacy checks.",
                produces=["bids_root", "conversion_manifest", "validator_summary"],
            )
        )
        steps.append(
            PlannedSkillRun(
                skill_name="bids_auditor",
                rationale="Converted datasets should be validated and summarized before further processing.",
                requires=["bids_root"],
                produces=["validator_json", "audit_report", "triage_checklist"],
            )
        )
        steps.append(
            PlannedSkillRun(
                skill_name="deid_check",
                rationale="Open-sharing readiness depends on privacy checks after BIDS conversion.",
                requires=["bids_root", "audit_report"],
                produces=["shareability_summary", "export_readiness_checklist"],
            )
        )
        handoffs.extend(
            [
                SkillHandoff(
                    from_skill="dicom_to_bids",
                    to_skill="bids_auditor",
                    required_artifacts=["bids_root", "conversion_manifest"],
                    rationale="Audit runs against the curated BIDS output.",
                ),
                SkillHandoff(
                    from_skill="bids_auditor",
                    to_skill="deid_check",
                    required_artifacts=["audit_report", "validator_json"],
                    rationale="Privacy review should surface validation blockers alongside shareability warnings.",
                ),
            ]
        )
    elif inspection.input_state.kind in {InputDatasetKind.BIDS, InputDatasetKind.DERIVATIVE}:
        steps.append(
            PlannedSkillRun(
                skill_name="bids_auditor",
                rationale="Existing BIDS inputs should be validated before downstream processing.",
                produces=["validator_json", "audit_report", "triage_checklist"],
            )
        )
        steps.append(
            PlannedSkillRun(
                skill_name="deid_check",
                rationale="Privacy readiness is required before any sharing claims.",
                requires=["bids_root", "audit_report"],
                produces=["shareability_summary", "export_readiness_checklist"],
            )
        )
        handoffs.append(
            SkillHandoff(
                from_skill="bids_auditor",
                to_skill="deid_check",
                required_artifacts=["audit_report", "validator_json"],
                rationale="The privacy review reuses the audited dataset state and validation findings.",
            )
        )

    return OrchestrationPlan(
        goal=goal,
        input_path=path,
        inspection=inspection,
        steps=steps,
        handoffs=handoffs,
        warnings=inspection.blockers,
    )
