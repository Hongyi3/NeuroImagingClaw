from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clawneuro.catalog import list_skills  # noqa: E402
from clawneuro.demo import run_foundation_demo  # noqa: E402
from clawneuro.routing import RoutingError, route_request  # noqa: E402


def cmd_list() -> int:
    for skill in list_skills():
        name = skill["name"]
        status = skill.get("status", "unknown")
        description = skill.get("description", "")
        print(f"{name:<24} [{status}] {description}")
    return 0


def cmd_show(skill_name: str) -> int:
    for skill in list_skills():
        if skill["name"] == skill_name:
            print(json.dumps(skill, indent=2))
            return 0
    print(f"Skill not found: {skill_name}", file=sys.stderr)
    return 1


def cmd_route(query: str, input_paths: list[str], trust_tier: str) -> int:
    try:
        decision = route_request(query=query, input_paths=input_paths, trust_tier=trust_tier)
        print(json.dumps(decision.to_dict(), indent=2))
        return 0
    except RoutingError as exc:
        print(json.dumps(exc.to_dict(), indent=2))
        return 1


def cmd_demo_foundation(output_dir: str) -> int:
    result = run_foundation_demo(Path(output_dir))
    print(
        json.dumps(
            {
                "status": "ok",
                "output_dir": str(Path(output_dir)),
                "selected_skill": result["summary"]["selected_skill"],
            },
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ClawNeuro repository helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List known skills")

    show = sub.add_parser("show", help="Show one catalog entry")
    show.add_argument("skill_name")

    route = sub.add_parser("route", help="Route a request to the best matching skill")
    route.add_argument("--query", required=True)
    route.add_argument("--input", action="append", default=[], dest="input_paths")
    route.add_argument(
        "--trust-tier",
        choices=["core", "reviewed-community", "experimental"],
        default="core",
    )
    route.add_argument("--json", action="store_true", help="Accepted for CLI stability")

    demo = sub.add_parser("demo", help="Run deterministic repository demos")
    demo_sub = demo.add_subparsers(dest="demo_command", required=True)
    foundation = demo_sub.add_parser("foundation", help="Run the Milestone 1 foundation demo")
    foundation.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.command == "list":
        return cmd_list()
    if args.command == "show":
        return cmd_show(args.skill_name)
    if args.command == "route":
        return cmd_route(args.query, args.input_paths, args.trust_tier)
    if args.command == "demo" and args.demo_command == "foundation":
        return cmd_demo_foundation(args.output)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
