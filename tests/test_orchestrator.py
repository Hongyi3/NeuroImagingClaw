from __future__ import annotations

from clawneuro.orchestrator import inspect_dataset, plan_phase1_workflow


def test_plan_phase1_for_bids_input(fixtures_root):
    bids_root = fixtures_root / "bids" / "minimal"
    inspection = inspect_dataset(bids_root)
    assert inspection.input_state.kind.value == "bids"
    assert "bids_auditor" in inspection.recommended_skills

    plan = plan_phase1_workflow(bids_root)
    assert [step.skill_name for step in plan.steps] == ["bids_auditor", "deid_check"]


def test_plan_phase1_for_dicom_input(fixtures_root):
    dicom_root = fixtures_root / "dicom" / "source"
    plan = plan_phase1_workflow(dicom_root)
    assert [step.skill_name for step in plan.steps] == [
        "dicom_to_bids",
        "bids_auditor",
        "deid_check",
    ]
