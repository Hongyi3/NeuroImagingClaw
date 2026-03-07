"""Execution planning and command capture for wrapped tools."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Optional, Sequence

from pydantic import Field

from clawneuro.core.errors import MissingToolError
from clawneuro.core.models import (
    ClawBaseModel,
    CommandRecord,
    ExecutionBackend,
    RunStatus,
    SoftwareInventoryRecord,
)

CONTAINER_INPUT_ROOT = Path("/clawneuro/input")
CONTAINER_OUTPUT_ROOT = Path("/clawneuro/output")
CONTAINER_CONFIG_ROOT = Path("/clawneuro/config")
CONTAINER_WORK_ROOT = Path("/clawneuro/work")
CONTAINER_LICENSE_ROOT = Path("/clawneuro/license")
CONTAINER_UPSTREAM_ROOT = Path("/clawneuro/upstream")


class BindMount(ClawBaseModel):
    """Container bind mount definition."""

    source: Path
    target: Path
    read_only: bool = True


class ExecutionRequest(ClawBaseModel):
    """Serializable command plan that can later be executed."""

    name: str
    backend: ExecutionBackend = ExecutionBackend.LOCAL_BINARY
    executable: str
    args: List[str] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    working_directory: Optional[Path] = None
    container_image: Optional[str] = None
    bind_mounts: List[BindMount] = Field(default_factory=list)
    description: Optional[str] = None
    use_container_entrypoint: bool = False

    def argv(self) -> List[str]:
        """Return the concrete argv for the requested backend."""

        if self.backend == ExecutionBackend.LOCAL_BINARY:
            return [self.executable] + self.args

        if self.backend == ExecutionBackend.DOCKER:
            if not self.container_image:
                raise MissingToolError("Docker execution requires a container image.")
            if not is_pinned_container_image(self.container_image):
                raise MissingToolError(
                    "Docker execution requires a pinned container image reference.",
                    context={"container_image": self.container_image},
                )
            argv = ["docker", "run", "--rm"]
            for mount in self.bind_mounts:
                mode = "ro" if mount.read_only else "rw"
                argv.extend(["-v", "{0}:{1}:{2}".format(mount.source, mount.target, mode)])
            for key, value in sorted(self.environment.items()):
                argv.extend(["-e", "{0}={1}".format(key, value)])
            argv.append(self.container_image)
            argv.extend(self.container_command())
            return argv

        if self.backend == ExecutionBackend.APPTAINER:
            if not self.container_image:
                raise MissingToolError("Apptainer execution requires an image path or URI.")
            if not is_pinned_container_image(self.container_image):
                raise MissingToolError(
                    "Apptainer execution requires a pinned container image reference.",
                    context={"container_image": self.container_image},
                )
            argv = ["apptainer", "exec"]
            for mount in self.bind_mounts:
                argv.extend(["--bind", "{0}:{1}".format(mount.source, mount.target)])
            argv.append(self.container_image)
            argv.extend(self.container_command())
            return argv

        raise MissingToolError(
            "Unsupported execution backend.",
            context={"backend": self.backend.value},
        )

    def container_command(self) -> List[str]:
        """Return the in-container command payload."""

        if self.use_container_entrypoint:
            return list(self.args)
        return [self.executable] + self.args

    def container_path(self, host_path: Path) -> Path:
        """Map a host path into the mounted in-container path."""

        resolved = host_path.resolve()
        for mount in self.bind_mounts:
            source = mount.source.resolve()
            if resolved == source:
                return mount.target
            if resolved.is_relative_to(source):
                return mount.target / resolved.relative_to(source)
        raise MissingToolError(
            "Path is not covered by this execution request's bind mounts.",
            context={"path": str(host_path), "bind_mounts": [mount.model_dump(mode="json") for mount in self.bind_mounts]},
        )

    def shell_command(self) -> str:
        """Render a shell-safe command string."""

        return " ".join(shlex.quote(part) for part in self.argv())


class ExecutionProvenanceEvidence(ClawBaseModel):
    """Structured runtime evidence collected for an execution request."""

    software: List[SoftwareInventoryRecord] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    complete: bool = True


def bidsapp_input_mount(source: Path) -> BindMount:
    """Return the canonical read-only BIDS input mount."""

    return BindMount(source=source, target=CONTAINER_INPUT_ROOT, read_only=True)


def bidsapp_output_mount(source: Path) -> BindMount:
    """Return the canonical read-write derivative output mount."""

    return BindMount(source=source, target=CONTAINER_OUTPUT_ROOT, read_only=False)


def bidsapp_work_mount(source: Path) -> BindMount:
    """Return the canonical read-write work directory mount."""

    return BindMount(source=source, target=CONTAINER_WORK_ROOT, read_only=False)


def bidsapp_config_file_mount(source: Path) -> tuple[BindMount, Path]:
    """Mount a config file's parent directory into the canonical config root."""

    return (
        BindMount(source=source.parent, target=CONTAINER_CONFIG_ROOT, read_only=True),
        CONTAINER_CONFIG_ROOT / source.name,
    )


def bidsapp_license_file_mount(source: Path) -> tuple[BindMount, Path]:
    """Mount a FreeSurfer license or similar file into the canonical license root."""

    return (
        BindMount(source=source.parent, target=CONTAINER_LICENSE_ROOT, read_only=True),
        CONTAINER_LICENSE_ROOT / source.name,
    )


def bidsapp_upstream_derivative_mount(source: Path, label: str) -> tuple[BindMount, Path]:
    """Mount an upstream derivative tree into a stable container path."""

    safe_label = "".join(character if character.isalnum() or character in {"-", "_", "."} else "-" for character in label)
    safe_label = safe_label.strip("-_.") or "derivatives"
    target = CONTAINER_UPSTREAM_ROOT / safe_label
    return (
        BindMount(source=source, target=target, read_only=True),
        target,
    )


def is_command_available(command: str) -> bool:
    """Return whether a binary is available on PATH."""

    return resolve_executable(command) is not None


def resolve_executable(
    command: str,
    environment: Optional[Dict[str, str]] = None,
) -> Optional[Path]:
    """Resolve a requested executable against the current or provided PATH."""

    if os.path.sep in command or (os.path.altsep and os.path.altsep in command):
        candidate = Path(command).expanduser()
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
        return None

    search_path = None
    if environment and environment.get("PATH"):
        search_path = environment["PATH"]
    resolved = shutil.which(command, path=search_path)
    return Path(resolved).resolve() if resolved else None


def prepend_executable_parent_to_path(
    executable: str,
    environment: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Prepend an executable's parent directory to PATH when a concrete path is supplied."""

    updated_environment = dict(environment or {})
    if os.path.sep not in executable and not (os.path.altsep and os.path.altsep in executable):
        return updated_environment

    parent = Path(executable).expanduser().parent
    if str(parent) in {"", "."}:
        return updated_environment

    current_path = updated_environment.get("PATH") or os.environ.get("PATH", "")
    updated_environment["PATH"] = (
        str(parent)
        if not current_path
        else os.pathsep.join([str(parent), current_path])
    )
    return updated_environment


def probe_command_version(
    command: str,
    environment: Optional[Dict[str, str]] = None,
    version_args: Optional[Sequence[Sequence[str]]] = None,
) -> Optional[str]:
    """Probe a local executable for its version string."""

    resolved = resolve_executable(command, environment=environment)
    if resolved is None:
        return None

    candidates = list(version_args or (["--version"],))
    for candidate in candidates:
        completed = subprocess.run(
            [str(resolved), *candidate],
            capture_output=True,
            check=False,
            text=True,
            env={**os.environ, **environment} if environment else None,
        )
        output = completed.stdout.strip() or completed.stderr.strip()
        if output:
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            for line in lines:
                lowered = line.lower()
                if "version" in lowered or (line.startswith("v") and len(line) > 1 and line[1].isdigit()):
                    return line
            return lines[0]
    return None


def _container_runtime_name(backend: ExecutionBackend) -> Optional[str]:
    if backend == ExecutionBackend.DOCKER:
        return "docker"
    if backend == ExecutionBackend.APPTAINER:
        return "apptainer"
    return None


def _container_image_version(image: Optional[str]) -> Optional[str]:
    if not image or "@sha256:" in image:
        return None
    last_segment = image.split("/")[-1]
    if ":" not in last_segment:
        return None
    return last_segment.rsplit(":", 1)[1]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _probe_docker_image_identifier(
    image: str,
    environment: Optional[Dict[str, str]] = None,
) -> tuple[Optional[str], List[str]]:
    notes: List[str] = []
    docker = resolve_executable("docker", environment=environment)
    if docker is None:
        notes.append("Docker image inspection could not run because the Docker executable was not resolved.")
        return None, notes

    repo_digests = subprocess.run(
        [str(docker), "image", "inspect", image, "--format", "{{json .RepoDigests}}"],
        capture_output=True,
        check=False,
        text=True,
        env={**os.environ, **environment} if environment else None,
    )
    if repo_digests.returncode == 0:
        output = repo_digests.stdout.strip()
        if output and output not in {"null", "<no value>"}:
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list) and parsed:
                return str(parsed[0]), notes

    image_id = subprocess.run(
        [str(docker), "image", "inspect", image, "--format", "{{json .Id}}"],
        capture_output=True,
        check=False,
        text=True,
        env={**os.environ, **environment} if environment else None,
    )
    if image_id.returncode == 0:
        output = image_id.stdout.strip()
        if output and output not in {"null", "<no value>"}:
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError:
                parsed = output
            if parsed:
                notes.append("Docker RepoDigests were unavailable; recorded the local image identifier instead.")
                return str(parsed), notes

    notes.append("Docker image digest or inspectable identifier could not be collected after execution.")
    return None, notes


def _probe_apptainer_image_identifier(image: str) -> tuple[Optional[str], List[str]]:
    candidate = Path(image).expanduser()
    if candidate.exists() and candidate.is_file():
        return _sha256_file(candidate), []
    return None, [
        "Apptainer image digest is only captured automatically for local image files; the configured image was not a local file path.",
    ]


def collect_execution_provenance_evidence(
    request: ExecutionRequest,
    *,
    tool_name: str,
    tool_role: str,
) -> ExecutionProvenanceEvidence:
    """Collect runtime/software provenance for a planned or executed request."""

    notes: List[str] = []

    if request.backend == ExecutionBackend.LOCAL_BINARY:
        version = probe_command_version(request.executable, environment=request.environment)
        resolved = resolve_executable(request.executable, environment=request.environment)
        complete = True
        if resolved is None:
            notes.append(
                "Local executable provenance is incomplete because the requested executable could not be resolved."
            )
            complete = False
        if version is None:
            notes.append(
                "Local executable provenance is incomplete because the wrapped tool version could not be probed."
            )
            complete = False
        return ExecutionProvenanceEvidence(
            software=[
                SoftwareInventoryRecord(
                    name=tool_name,
                    version=version,
                    role=tool_role,
                    source=str(resolved) if resolved is not None else None,
                )
            ],
            notes=notes,
            complete=complete,
        )

    runtime_name = _container_runtime_name(request.backend)
    runtime_version = probe_command_version(runtime_name, environment=request.environment) if runtime_name else None
    resolved_runtime = (
        resolve_executable(runtime_name, environment=request.environment) if runtime_name else None
    )
    container_identifier = None
    complete = True

    if runtime_name is None:
        notes.append("Container provenance is incomplete because the execution backend is unsupported.")
        complete = False
    else:
        if resolved_runtime is None:
            notes.append(
                f"Container provenance is incomplete because the {runtime_name} executable could not be resolved."
            )
            complete = False
        if runtime_version is None:
            notes.append(
                f"Container provenance is incomplete because the {runtime_name} version could not be probed."
            )
            complete = False

    if not request.container_image:
        notes.append("Container provenance is incomplete because no container image reference was recorded.")
        complete = False
    else:
        if request.backend == ExecutionBackend.DOCKER:
            container_identifier, inspect_notes = _probe_docker_image_identifier(
                request.container_image,
                environment=request.environment,
            )
        else:
            container_identifier, inspect_notes = _probe_apptainer_image_identifier(request.container_image)
        notes.extend(inspect_notes)
        if container_identifier is None:
            complete = False

    return ExecutionProvenanceEvidence(
        software=[
            SoftwareInventoryRecord(
                name=runtime_name or "container-runtime",
                version=runtime_version,
                role="container-runtime",
                source=str(resolved_runtime) if resolved_runtime is not None else None,
            ),
            SoftwareInventoryRecord(
                name=tool_name,
                version=_container_image_version(request.container_image),
                role=tool_role,
                container_image=request.container_image,
                container_digest=container_identifier,
            ),
        ],
        notes=notes,
        complete=complete,
    )


def is_pinned_container_image(image: str) -> bool:
    """Return whether a container reference is pinned to a tag or digest."""

    if "@sha256:" in image:
        return True
    last_segment = image.split("/")[-1]
    if ":" not in last_segment:
        return False
    tag = last_segment.rsplit(":", 1)[1]
    return bool(tag) and tag.lower() != "latest"


def planned_command_record(request: ExecutionRequest) -> CommandRecord:
    """Create a planned command record without executing anything."""

    return CommandRecord(
        name=request.name,
        backend=request.backend,
        argv=request.argv(),
        shell_command=request.shell_command(),
        working_directory=request.working_directory,
        environment=request.environment,
        status=RunStatus.PLANNED,
    )


def execute_request(
    request: ExecutionRequest,
    stdout_path: Optional[Path] = None,
    stderr_path: Optional[Path] = None,
) -> CommandRecord:
    """Execute a request and return a populated command record."""

    runtime = request.argv()[0]
    resolved_runtime = resolve_executable(runtime, environment=request.environment)
    if resolved_runtime is None:
        raise MissingToolError(
            "Required runtime is not available.",
            context={
                "runtime": runtime,
                "resolved_runtime": None,
                "request": request.model_dump(mode="json"),
            },
        )

    if stdout_path:
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
    if stderr_path:
        stderr_path.parent.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc)
    started_perf = perf_counter()
    completed = subprocess.run(
        request.argv(),
        capture_output=True,
        cwd=request.working_directory,
        env={**os.environ, **request.environment} if request.environment else None,
        text=True,
        check=False,
    )
    finished = datetime.now(timezone.utc)
    duration = perf_counter() - started_perf

    if stdout_path:
        stdout_path.write_text(completed.stdout, encoding="utf-8")
    if stderr_path:
        stderr_path.write_text(completed.stderr, encoding="utf-8")

    status = RunStatus.SUCCEEDED if completed.returncode == 0 else RunStatus.FAILED

    return CommandRecord(
        name=request.name,
        backend=request.backend,
        argv=request.argv(),
        shell_command=request.shell_command(),
        working_directory=request.working_directory,
        environment=request.environment,
        status=status,
        exit_code=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        started_at=started,
        finished_at=finished,
        duration_seconds=duration,
    )
