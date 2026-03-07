"""Report assembly and rendering utilities."""

from clawneuro.reporting.harvest import (
    HarvestedOutputs,
    harvested_output_artifacts,
    harvest_fmriprep_outputs,
    harvest_mriqc_outputs,
)
from clawneuro.reporting.models import ReportBundleDraft, ReportSection
from clawneuro.reporting.renderers import (
    aggregate_warnings,
    assemble_execution_report,
    build_artifact_index,
    render_markdown_report,
    render_methods_text,
)

__all__ = [
    "HarvestedOutputs",
    "ReportBundleDraft",
    "ReportSection",
    "aggregate_warnings",
    "assemble_execution_report",
    "build_artifact_index",
    "harvest_fmriprep_outputs",
    "harvest_mriqc_outputs",
    "harvested_output_artifacts",
    "render_markdown_report",
    "render_methods_text",
]
