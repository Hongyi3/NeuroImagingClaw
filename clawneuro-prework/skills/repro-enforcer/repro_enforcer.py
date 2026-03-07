from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clawneuro.provenance import bundle_existing_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a ClawNeuro reproducibility bundle")
    parser.add_argument("--report", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--command", action="append", default=[])
    args = parser.parse_args()

    result = bundle_existing_outputs(
        report_path=Path(args.report),
        result_path=Path(args.result),
        output_dir=Path(args.output),
        commands=args.command
        or [
            "python skills/repro-enforcer/repro_enforcer.py --report report.md --result result.json --output OUTPUT_DIR"
        ],
        random_seeds={"repro_enforcer": 0},
    )
    print(json.dumps({"status": "ok", "output_dir": args.output, "skill": result["skill"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
