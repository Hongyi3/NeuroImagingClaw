"""BIDS-aware helpers used by intake, audit, and reporting code."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from clawneuro.core.config import write_model_json
from clawneuro.core.errors import InvalidInputStateError
from clawneuro.core.models import (
    DerivativeDatasetDescription,
    GeneratedByRecord,
    InputDatasetKind,
    DatasetInventory,
    SkillInputState,
)

MODALITY_DIRS = {
    "anat": "anat",
    "func": "bold",
    "dwi": "dwi",
    "fmap": "fmap",
    "perf": "perf",
    "pet": "pet",
}
DICOM_SUFFIXES = {".dcm", ".ima"}


def _iter_subject_dirs(root: Path) -> Iterable[Path]:
    return sorted(path for path in root.iterdir() if path.is_dir() and path.name.startswith("sub-"))


def _load_dataset_description(path: Path) -> Dict[str, object]:
    dataset_description = path / "dataset_description.json"
    if not dataset_description.exists():
        return {}
    return json.loads(dataset_description.read_text(encoding="utf-8"))


def detect_input_state(root: Path) -> SkillInputState:
    """Classify a path as BIDS, DICOM-like, derivative, or unknown."""

    readable = root.exists() and root.is_dir()
    if not readable:
        return SkillInputState(root=root, kind=InputDatasetKind.UNKNOWN, readable=False)

    dataset_description = root / "dataset_description.json"
    sub_dirs = list(_iter_subject_dirs(root))
    dicom_like = any(
        file_path.suffix.lower() in DICOM_SUFFIXES or file_path.name.upper().endswith(".IMA")
        for file_path in root.rglob("*")
        if file_path.is_file()
    )
    is_derivative = "derivatives" in root.parts or (
        dataset_description.exists()
        and _load_dataset_description(root).get("DatasetType") == "derivative"
    )

    if dataset_description.exists() or sub_dirs:
        inventory = inspect_bids_dataset(root)
        kind = InputDatasetKind.DERIVATIVE if is_derivative else InputDatasetKind.BIDS
        return SkillInputState(
            root=root,
            kind=kind,
            readable=True,
            dataset_description_present=dataset_description.exists(),
            contains_dicom=dicom_like,
            modalities=inventory.modalities,
            participant_ids=inventory.subject_ids,
            notes=[],
        )

    if dicom_like:
        return SkillInputState(
            root=root,
            kind=InputDatasetKind.DICOM,
            readable=True,
            contains_dicom=True,
            notes=["Directory contains files with DICOM-like suffixes."],
        )

    return SkillInputState(
        root=root,
        kind=InputDatasetKind.UNKNOWN,
        readable=True,
        notes=["Path is readable but does not look like a BIDS dataset or DICOM source."],
    )


def inspect_bids_dataset(root: Path) -> DatasetInventory:
    """Build a lightweight inventory of a BIDS dataset."""

    if not root.exists() or not root.is_dir():
        raise InvalidInputStateError(
            "BIDS root is not a readable directory.",
            context={"path": str(root)},
        )

    dataset_description_path = root / "dataset_description.json"
    description = _load_dataset_description(root)
    subject_ids: List[str] = []
    session_ids: Set[str] = set()
    modalities: Set[str] = set()
    files_by_modality: Dict[str, int] = {}
    file_count = 0

    for subject_dir in _iter_subject_dirs(root):
        subject_ids.append(subject_dir.name)
        for child in subject_dir.rglob("*"):
            if child.is_file():
                file_count += 1
            if child.is_dir() and child.name.startswith("ses-"):
                session_ids.add(child.name)
            if child.is_dir() and child.name in MODALITY_DIRS:
                modality = MODALITY_DIRS[child.name]
                modalities.add(modality)
                files_by_modality.setdefault(modality, 0)
                files_by_modality[modality] += sum(1 for file_path in child.rglob("*") if file_path.is_file())

    dataset_name = str(description.get("Name") or root.name)
    dataset_type = str(description.get("DatasetType") or "raw")
    readme_path = root / "README"
    if not readme_path.exists():
        readme_path = root / "README.md"
    if not readme_path.exists():
        readme_path = None  # type: ignore[assignment]

    return DatasetInventory(
        root=root,
        dataset_name=dataset_name,
        dataset_type=dataset_type,
        subject_ids=subject_ids,
        session_ids=sorted(session_ids),
        modalities=sorted(modalities),
        files_by_modality=dict(sorted(files_by_modality.items())),
        file_count=file_count,
        has_dataset_description=dataset_description_path.exists(),
        dataset_description_path=dataset_description_path if dataset_description_path.exists() else None,
        dataset_readme_path=readme_path,
    )


def build_derivative_dataset_description(
    name: str,
    generated_by: List[GeneratedByRecord],
    source_datasets: Optional[List[Dict[str, str]]] = None,
) -> DerivativeDatasetDescription:
    """Create a minimal BIDS Derivatives dataset description."""

    return DerivativeDatasetDescription(
        name=name,
        GeneratedBy=generated_by,
        SourceDatasets=source_datasets or [],
    )


def write_derivative_dataset_description(
    path: Path,
    description: DerivativeDatasetDescription,
) -> Path:
    """Write a derivative dataset description JSON file."""

    return write_model_json(path, description)
