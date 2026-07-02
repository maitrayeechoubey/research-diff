"""CLI entry point for research-diff."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from .client import MockPerplexityClient, PerplexityClient
from .diff import diff_snapshots
from .digest import render_digest
from .store import DEFAULT_ROOT, ResearchObject, list_objects


def cmd_track(args: argparse.Namespace) -> int:
    obj = ResearchObject(DEFAULT_ROOT, args.name)
    if obj.exists:
        print(f"'{args.name}' is already tracked. Use `research-diff run {args.name}`.", file=sys.stderr)
        return 1
    obj.create(query=args.query, mock_fixture=args.mock_fixture)
    print(f"Tracking '{args.name}': {args.query!r}")
    if args.mock_fixture:
        print(f"  (mock mode, replaying fixtures from {args.mock_fixture})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    obj = ResearchObject(DEFAULT_ROOT, args.name)
    if not obj.exists:
        print(f"'{args.name}' is not tracked. Run `research-diff track {args.name} --query ...` first.", file=sys.stderr)
        return 1

    meta = obj.load_meta()
    call_index = obj.call_count()

    if meta.get("mock_fixture"):
        client = MockPerplexityClient(Path(meta["mock_fixture"]))
        result = client.search(meta["query"], call_index=call_index)
    else:
        client = PerplexityClient()
        result = client.search(meta["query"])

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prior_paths = obj.snapshot_paths()
    obj.save_snapshot(result, timestamp)

    if not prior_paths:
        print(f"First snapshot saved for '{args.name}' ({timestamp}). Nothing to diff against yet.")
        return 0

    old_result = obj.load_snapshot(prior_paths[-1])
    diff = diff_snapshots(old_result, result)
    print(render_digest(args.name, meta["query"], timestamp, diff))
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    obj = ResearchObject(DEFAULT_ROOT, args.name)
    if not obj.exists:
        print(f"'{args.name}' is not tracked.", file=sys.stderr)
        return 1
    paths = obj.snapshot_paths()
    if not paths:
        print("No snapshots yet.")
        return 0
    for p in paths:
        print(p.stem)
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    obj = ResearchObject(DEFAULT_ROOT, args.name)
    if not obj.exists:
        print(f"'{args.name}' is not tracked.", file=sys.stderr)
        return 1
    paths = obj.snapshot_paths()
    if len(paths) < 2:
        print("Need at least 2 snapshots to diff.", file=sys.stderr)
        return 1

    from_path = next((p for p in paths if p.stem == args.from_ts), paths[-2])
    to_path = next((p for p in paths if p.stem == args.to_ts), paths[-1])

    old_result = obj.load_snapshot(from_path)
    new_result = obj.load_snapshot(to_path)
    diff = diff_snapshots(old_result, new_result)
    meta = obj.load_meta()
    print(render_digest(args.name, meta["query"], to_path.stem, diff))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    names = list_objects(DEFAULT_ROOT)
    if not names:
        print("No tracked research objects yet.")
        return 0
    for name in names:
        obj = ResearchObject(DEFAULT_ROOT, name)
        meta = obj.load_meta()
        print(f"{name}: {meta['query']!r} ({obj.call_count()} snapshots)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-diff",
        description="Track a Perplexity query as a persistent, versioned research object and see what changed over time.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_track = sub.add_parser("track", help="Start tracking a new research query")
    p_track.add_argument("name")
    p_track.add_argument("--query", required=True)
    p_track.add_argument(
        "--mock-fixture",
        help="Path to a fixtures/<topic> directory to replay instead of calling the live API",
    )
    p_track.set_defaults(func=cmd_track)

    p_run = sub.add_parser("run", help="Execute the tracked query and diff against the previous run")
    p_run.add_argument("name")
    p_run.set_defaults(func=cmd_run)

    p_history = sub.add_parser("history", help="List snapshot timestamps for a tracked query")
    p_history.add_argument("name")
    p_history.set_defaults(func=cmd_history)

    p_diff = sub.add_parser("diff", help="Diff two specific snapshots (defaults to the last two)")
    p_diff.add_argument("name")
    p_diff.add_argument("--from", dest="from_ts", default=None)
    p_diff.add_argument("--to", dest="to_ts", default=None)
    p_diff.set_defaults(func=cmd_diff)

    p_list = sub.add_parser("list", help="List all tracked research objects")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
