from __future__ import annotations

import json

from clawneuro.core import GeneratedByRecord, build_derivative_dataset_description, ensure_run_layout
from clawneuro.core.bids import write_derivative_dataset_description


def test_run_layout_creation_and_derivative_description(tmp_path):
    layout = ensure_run_layout(tmp_path / "run")
    assert layout.report_dir.exists()
    assert layout.manifests_dir.exists()
    assert layout.logs_dir.exists()
    assert layout.provenance_dir.exists()
    assert layout.derivatives_dir.exists()

    description = build_derivative_dataset_description(
        name="ClawNeuro Derivatives",
        generated_by=[GeneratedByRecord(name="clawneuro", version="0.1.0")],
        source_datasets=[{"URL": "https://openneuro.org/datasets/ds000001"}],
    )
    description_path = write_derivative_dataset_description(
        layout.derivatives_dir / "dataset_description.json",
        description,
    )
    data = json.loads(description_path.read_text(encoding="utf-8"))
    assert data["DatasetType"] == "derivative"
    assert data["GeneratedBy"][0]["name"] == "clawneuro"
