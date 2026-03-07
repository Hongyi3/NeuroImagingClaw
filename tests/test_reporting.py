from __future__ import annotations

from pathlib import Path

from clawneuro.core import (
    DatasetInventory,
    ProvenanceRecord,
    RunManifest,
    RunStatus,
    SkillDescriptor,
    SkillInputState,
    SkillKind,
    SoftwareInventoryRecord,
)
from clawneuro.core.models import InputDatasetKind
from clawneuro.reporting import assemble_execution_report, render_markdown_report, render_methods_text


def _manifest():
    return RunManifest(
        skill=SkillDescriptor(name="bids_auditor", kind=SkillKind.AUDIT),
        status=RunStatus.PLANNED,
        input_state=SkillInputState(root=Path("."), kind=InputDatasetKind.BIDS, readable=True),
        dataset_inventory=DatasetInventory(
            root=Path("."),
            dataset_name="demo-dataset",
            subject_ids=["sub-01"],
            modalities=["anat", "bold"],
        ),
        result_summary="Audit planned.",
        provenance=ProvenanceRecord(
            software=[SoftwareInventoryRecord(name="bids-validator", version="1.14.0")]
        ),
    )


def test_render_methods_text_and_markdown_bundle():
    manifest = _manifest()
    methods = render_methods_text(manifest)
    assert "bids_auditor" in methods
    assert "demo-dataset" in methods

    bundle = assemble_execution_report([manifest])
    markdown = render_markdown_report(bundle)
    assert "# ClawNeuro Execution Report" in markdown
    assert "Methods:" in markdown
