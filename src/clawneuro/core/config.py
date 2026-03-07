"""Configuration loading and serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Type, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from clawneuro.core.errors import ConfigurationError

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ path is primary
    import tomli as tomllib  # type: ignore[no-redef]

ModelT = TypeVar("ModelT", bound=BaseModel)


def load_raw_config(path: Path) -> Dict[str, Any]:
    """Load a configuration file into a dictionary."""

    if not path.exists():
        raise ConfigurationError("Configuration file does not exist.", context={"path": str(path)})

    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8")

    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(content) or {}
    elif suffix == ".json":
        data = json.loads(content)
    elif suffix == ".toml":
        data = tomllib.loads(content)
    else:
        raise ConfigurationError(
            "Unsupported configuration format.",
            context={"path": str(path), "suffix": suffix},
        )

    if not isinstance(data, dict):
        raise ConfigurationError(
            "Configuration root must be a mapping.",
            context={"path": str(path)},
        )

    return data


def load_config(path: Path, model_type: Type[ModelT]) -> ModelT:
    """Load and validate configuration using a Pydantic model."""

    try:
        return model_type.model_validate(load_raw_config(path))
    except ValidationError as exc:
        raise ConfigurationError(
            "Configuration validation failed.",
            context={"path": str(path), "errors": exc.errors()},
        ) from exc


def dump_model(model: BaseModel) -> Dict[str, Any]:
    """Return a JSON-safe dictionary for deterministic serialization."""

    return model.model_dump(mode="json", by_alias=True)


def write_model_json(path: Path, model: BaseModel) -> Path:
    """Write a Pydantic model to JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dump_model(model), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def write_model_yaml(path: Path, model: BaseModel) -> Path:
    """Write a Pydantic model to YAML with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(dump_model(model), sort_keys=True, allow_unicode=False),
        encoding="utf-8",
    )
    return path
