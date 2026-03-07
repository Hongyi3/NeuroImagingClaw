"""Execution planning and command capture for wrapped tools."""

from __future__ import annotations

import shlex
import shutil
import subprocess
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Optional

from pydantic import Field

from clawneuro.core.errors import MissingToolError
from clawneuro.core.models import ClawBaseModel, CommandRecord, ExecutionBackend, RunStatus


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

    def argv(self) -> List[str]:
        """Return the concrete argv for the requested backend."""

        if self.backend == ExecutionBackend.LOCAL_BINARY:
            return [self.executable] + self.args

        if self.backend == ExecutionBackend.DOCKER:
            if not self.container_image:
                raise MissingToolError("Docker execution requires a container image.")
            argv = ["docker", "run", "--rm"]
            for mount in self.bind_mounts:
                mode = "ro" if mount.read_only else "rw"
                argv.extend(["-v", "{0}:{1}:{2}".format(mount.source, mount.target, mode)])
            for key, value in sorted(self.environment.items()):
                argv.extend(["-e", "{0}={1}".format(key, value)])
            argv.append(self.container_image)
            argv.append(self.executable)
            argv.extend(self.args)
            return argv

        if self.backend == ExecutionBackend.APPTAINER:
            if not self.container_image:
                raise MissingToolError("Apptainer execution requires an image path or URI.")
            argv = ["apptainer", "exec"]
            for mount in self.bind_mounts:
                argv.extend(["--bind", "{0}:{1}".format(mount.source, mount.target)])
            argv.append(self.container_image)
            argv.append(self.executable)
            argv.extend(self.args)
            return argv

        raise MissingToolError(
            "Unsupported execution backend.",
            context={"backend": self.backend.value},
        )

    def shell_command(self) -> str:
        """Render a shell-safe command string."""

        return " ".join(shlex.quote(part) for part in self.argv())


def is_command_available(command: str) -> bool:
    """Return whether a binary is available on PATH."""

    return shutil.which(command) is not None


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
    if not is_command_available(runtime):
        raise MissingToolError(
            "Required runtime is not available.",
            context={"runtime": runtime, "request": request.model_dump(mode="json")},
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
