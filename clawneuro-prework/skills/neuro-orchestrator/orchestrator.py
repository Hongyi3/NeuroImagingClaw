from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clawneuro.routing import RoutingError, route_request  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a request to a ClawNeuro skill")
    parser.add_argument("--query", required=True)
    parser.add_argument("--input", action="append", default=[], dest="input_paths")
    parser.add_argument(
        "--trust-tier",
        choices=["core", "reviewed-community", "experimental"],
        default="core",
    )
    args = parser.parse_args()

    try:
        decision = route_request(
            query=args.query,
            input_paths=args.input_paths,
            trust_tier=args.trust_tier,
        )
        print(json.dumps(decision.to_dict(), indent=2))
        return 0
    except RoutingError as exc:
        print(json.dumps(exc.to_dict(), indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
