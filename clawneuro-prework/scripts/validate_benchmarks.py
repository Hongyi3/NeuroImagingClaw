from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clawneuro.benchmarks import validate_benchmark_manifest  # noqa: E402
from clawneuro.catalog import discover_skill_specs  # noqa: E402


def main() -> int:
    skill_specs = discover_skill_specs()
    benchmarks = validate_benchmark_manifest(
        known_skill_names={skill.name for skill in skill_specs},
        skill_specs=skill_specs,
    )
    print(f"Validated {len(benchmarks)} benchmark entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
