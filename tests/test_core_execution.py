from __future__ import annotations

from pathlib import Path

import pytest

from clawneuro.core import (
    BindMount,
    CONTAINER_CONFIG_ROOT,
    CONTAINER_INPUT_ROOT,
    CONTAINER_LICENSE_ROOT,
    CONTAINER_OUTPUT_ROOT,
    CONTAINER_UPSTREAM_ROOT,
    CONTAINER_WORK_ROOT,
    ExecutionBackend,
    ExecutionProvenanceEvidence,
    ExecutionRequest,
    bidsapp_config_file_mount,
    bidsapp_license_file_mount,
    bidsapp_upstream_derivative_mount,
    bidsapp_work_mount,
    collect_execution_provenance_evidence,
    prepend_executable_parent_to_path,
    probe_command_version,
    resolve_executable,
)
from clawneuro.core.errors import MissingToolError


def _write_stub_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def test_docker_request_uses_container_entrypoint_and_stable_mounts():
    request = ExecutionRequest(
        name="dcm2bids",
        backend=ExecutionBackend.DOCKER,
        executable="dcm2bids",
        args=["-d", str(CONTAINER_INPUT_ROOT), "-o", str(CONTAINER_OUTPUT_ROOT), "-c", str(CONTAINER_CONFIG_ROOT / "config.json")],
        container_image="unfmontreal/dcm2bids:3.2.0",
        bind_mounts=[
            BindMount(source=Path("/tmp/input"), target=CONTAINER_INPUT_ROOT, read_only=True),
            BindMount(source=Path("/tmp/output"), target=CONTAINER_OUTPUT_ROOT, read_only=False),
            BindMount(source=Path("/tmp/config"), target=CONTAINER_CONFIG_ROOT, read_only=True),
        ],
        use_container_entrypoint=True,
    )

    assert request.argv() == [
        "docker",
        "run",
        "--rm",
        "-v",
        "/tmp/input:/clawneuro/input:ro",
        "-v",
        "/tmp/output:/clawneuro/output:rw",
        "-v",
        "/tmp/config:/clawneuro/config:ro",
        "unfmontreal/dcm2bids:3.2.0",
        "-d",
        "/clawneuro/input",
        "-o",
        "/clawneuro/output",
        "-c",
        "/clawneuro/config/config.json",
    ]


def test_apptainer_request_uses_bind_mounts():
    request = ExecutionRequest(
        name="bids-validator",
        backend=ExecutionBackend.APPTAINER,
        executable="bids-validator-deno",
        args=[str(CONTAINER_INPUT_ROOT), "--format", "json"],
        container_image="docker://ghcr.io/bids-standard/bids-validator:v2.4.1",
        bind_mounts=[
            BindMount(source=Path("/tmp/input"), target=CONTAINER_INPUT_ROOT, read_only=True),
        ],
        use_container_entrypoint=True,
    )

    assert request.argv() == [
        "apptainer",
        "exec",
        "--bind",
        "/tmp/input:/clawneuro/input",
        "docker://ghcr.io/bids-standard/bids-validator:v2.4.1",
        "/clawneuro/input",
        "--format",
        "json",
    ]


def test_container_path_maps_host_paths():
    request = ExecutionRequest(
        name="validator",
        backend=ExecutionBackend.DOCKER,
        executable="bids-validator-deno",
        args=[],
        container_image="ghcr.io/bids-standard/bids-validator:v2.4.1",
        bind_mounts=[
            BindMount(source=Path("/tmp/input"), target=CONTAINER_INPUT_ROOT, read_only=True),
        ],
        use_container_entrypoint=True,
    )

    assert request.container_path(Path("/tmp/input/sub-01/anat/sub-01_T1w.nii")) == (
        CONTAINER_INPUT_ROOT / "sub-01" / "anat" / "sub-01_T1w.nii"
    )


def test_unpinned_container_images_are_rejected():
    request = ExecutionRequest(
        name="validator",
        backend=ExecutionBackend.DOCKER,
        executable="bids-validator-deno",
        args=[],
        container_image="ghcr.io/bids-standard/bids-validator:latest",
        use_container_entrypoint=True,
    )

    with pytest.raises(MissingToolError):
        request.argv()


def test_prepend_executable_parent_to_path_preserves_existing_path(tmp_path):
    executable = tmp_path / "tools" / "dcm2niix"
    executable.parent.mkdir()
    executable.write_text("", encoding="utf-8")

    environment = prepend_executable_parent_to_path(
        str(executable),
        environment={"PATH": "/usr/bin"},
    )

    assert environment["PATH"].split(":")[0] == str(executable.parent)
    assert environment["PATH"].endswith("/usr/bin")


def test_resolve_executable_uses_provided_environment_path(tmp_path):
    executable = _write_stub_executable(
        tmp_path / "stub-tool",
        "#!/bin/sh\nexit 0\n",
    )

    resolved = resolve_executable(
        "stub-tool",
        environment={"PATH": str(tmp_path)},
    )

    assert resolved == executable.resolve()


def test_probe_command_version_returns_first_output_line(tmp_path):
    executable = _write_stub_executable(
        tmp_path / "stub-tool",
        "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then\n  echo 'stub-tool 1.2.3'\n  echo 'extra line'\n  exit 0\nfi\nexit 1\n",
    )

    version = probe_command_version(
        str(executable),
        version_args=[["--version"]],
    )

    assert version == "stub-tool 1.2.3"


def test_probe_command_version_accepts_nonzero_exit_when_version_is_reported(tmp_path):
    executable = _write_stub_executable(
        tmp_path / "nonzero-version-tool",
        "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then\n  echo 'notice line'\n  echo 'version 9.9.9'\n  exit 3\nfi\nexit 1\n",
    )

    version = probe_command_version(
        str(executable),
        version_args=[["--version"]],
    )

    assert version == "version 9.9.9"


def test_bidsapp_file_and_work_mount_helpers_use_stable_paths(tmp_path):
    config_file = tmp_path / "config" / "filters.json"
    config_file.parent.mkdir()
    config_file.write_text("{}\n", encoding="utf-8")
    license_file = tmp_path / "license" / "license.txt"
    license_file.parent.mkdir()
    license_file.write_text("stub\n", encoding="utf-8")
    reuse_root = tmp_path / "reuse"
    reuse_root.mkdir()
    work_root = tmp_path / "work"
    work_root.mkdir()

    config_mount, config_path = bidsapp_config_file_mount(config_file)
    license_mount, license_path = bidsapp_license_file_mount(license_file)
    reuse_mount, reuse_path = bidsapp_upstream_derivative_mount(reuse_root, "reuse-1")
    work_mount = bidsapp_work_mount(work_root)

    assert config_mount.target == CONTAINER_CONFIG_ROOT
    assert config_path == CONTAINER_CONFIG_ROOT / "filters.json"
    assert license_mount.target == CONTAINER_LICENSE_ROOT
    assert license_path == CONTAINER_LICENSE_ROOT / "license.txt"
    assert reuse_mount.target == CONTAINER_UPSTREAM_ROOT / "reuse-1"
    assert reuse_path == CONTAINER_UPSTREAM_ROOT / "reuse-1"
    assert work_mount.target == CONTAINER_WORK_ROOT
    assert work_mount.read_only is False


def test_collect_execution_provenance_evidence_for_docker_captures_runtime_and_image_identifier(tmp_path):
    docker = _write_stub_executable(
        tmp_path / "docker",
        (
            "#!/bin/sh\n"
            "if [ \"$1\" = \"--version\" ]; then\n"
            "  echo 'Docker version 26.1.0, build deadbeef'\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"image\" ] && [ \"$2\" = \"inspect\" ] && [ \"$4\" = \"--format\" ]; then\n"
            "  if [ \"$5\" = '{{json .RepoDigests}}' ]; then\n"
            "    echo '[\"nipreps/mriqc@sha256:123abc\"]'\n"
            "    exit 0\n"
            "  fi\n"
            "  if [ \"$5\" = '{{json .Id}}' ]; then\n"
            "    echo '\"sha256:local-image-id\"'\n"
            "    exit 0\n"
            "  fi\n"
            "fi\n"
            "exit 1\n"
        ),
    )

    evidence = collect_execution_provenance_evidence(
        ExecutionRequest(
            name="mriqc-participant",
            backend=ExecutionBackend.DOCKER,
            executable="mriqc",
            args=["/clawneuro/input", "/clawneuro/output", "participant"],
            container_image="nipreps/mriqc:24.0.0",
            bind_mounts=[BindMount(source=Path("/tmp/input"), target=CONTAINER_INPUT_ROOT)],
            use_container_entrypoint=True,
            environment={"PATH": str(tmp_path)},
        ),
        tool_name="mriqc",
        tool_role="qc",
    )

    assert isinstance(evidence, ExecutionProvenanceEvidence)
    assert evidence.complete is True
    assert evidence.software[0].name == "docker"
    assert evidence.software[0].source == str(docker.resolve())
    assert evidence.software[1].name == "mriqc"
    assert evidence.software[1].container_digest == "nipreps/mriqc@sha256:123abc"


def test_collect_execution_provenance_evidence_reports_missing_container_identifier():
    evidence = collect_execution_provenance_evidence(
        ExecutionRequest(
            name="mriqc-participant",
            backend=ExecutionBackend.DOCKER,
            executable="mriqc",
            args=["/clawneuro/input", "/clawneuro/output", "participant"],
            container_image="nipreps/mriqc:24.0.0",
            use_container_entrypoint=True,
        ),
        tool_name="mriqc",
        tool_role="qc",
    )

    assert evidence.complete is False
    assert any("docker executable could not be resolved" in note.lower() for note in evidence.notes)
    assert evidence.software[1].container_digest is None
