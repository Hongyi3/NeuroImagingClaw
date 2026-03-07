from __future__ import annotations

from pathlib import Path

from clawneuro.core import (
    DatasetInventory,
    InputDatasetKind,
    ProvenanceRecord,
    RunManifest,
    RunStatus,
    SkillDescriptor,
    SkillInputState,
    SkillKind,
)
from clawneuro.core.layout import ensure_run_layout
from clawneuro.provenance import write_provenance_bundle


def test_write_provenance_bundle_creates_minimum_files(tmp_path):
    layout = ensure_run_layout(tmp_path / "run")
    payload = layout.report_dir / "summary.txt"
    payload.write_text("summary\n", encoding="utf-8")

    manifest = RunManifest(
        skill=SkillDescriptor(name="test-skill", kind=SkillKind.AUDIT),
        status=RunStatus.SUCCEEDED,
        input_state=SkillInputState(root=tmp_path, kind=InputDatasetKind.BIDS, readable=True),
        dataset_inventory=DatasetInventory(root=tmp_path, dataset_name="fixture"),
        result_summary="Finished test run.",
        provenance=ProvenanceRecord(),
    )

    provenance = write_provenance_bundle(layout, manifest, artifact_paths=[payload], notes=["unit test"])
    assert (layout.provenance_dir / "commands.sh").exists()
    assert (layout.provenance_dir / "environment.yml").exists()
    assert (layout.provenance_dir / "analysis_log.md").exists()
    assert (layout.provenance_dir / "checksums.sha256").exists()
    assert provenance.output_checksums
