#!/usr/bin/env python3
"""Run Phase 1 holdout suite for Baseline A, B, and merged (C)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
NOTEBOOKS = REPO_ROOT / "notebooks"
sys.path.insert(0, str(SCRIPTS))

from env_paths import get_paths
from holdout_runner import (
    PHASE1_OPPONENTS,
    load_baseline_agent,
    load_deck,
    run_holdout_suite,
    summarize_holdout,
)

BASELINE_CHOICES = ("baseline_a", "baseline_b", "baseline_merged")

AGENT_PATHS = {
    "baseline_a": NOTEBOOKS / "agents" / "main_baseline_a.py",
    "baseline_b": NOTEBOOKS / "agents" / "main_baseline_b.py",
    "baseline_merged": NOTEBOOKS / "agents" / "main_baseline_merged.py",
}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge_summaries(existing: list[dict], new_rows: list[dict]) -> list[dict]:
    """Replace summaries for baselines present in new_rows; keep others."""
    by_key = {(r["baseline"], r["opponent"]): r for r in existing}
    for row in new_rows:
        by_key[(row["baseline"], row["opponent"])] = row
    order = ["baseline_a", "baseline_b", "baseline_merged"]
    out: list[dict] = []
    for baseline in order:
        for opponent in PHASE1_OPPONENTS:
            key = (baseline, opponent)
            if key in by_key:
                out.append(by_key[key])
    for key, row in by_key.items():
        if key[0] not in order:
            out.append(row)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 local holdout evaluation")
    parser.add_argument("--games", type=int, default=40, help="Games per opponent (default: 40)")
    parser.add_argument(
        "--baselines",
        nargs="+",
        default=["baseline_a", "baseline_b"],
        choices=list(BASELINE_CHOICES),
    )
    parser.add_argument(
        "--merge-latest",
        action="store_true",
        help="Merge new summaries into phase1_holdout_summary_latest.json (keep other baselines)",
    )
    args = parser.parse_args()

    paths = get_paths()
    paths.ensure_dirs()
    cg_parent = paths.cg_dir.parent if paths.cg_dir else None
    our_deck = load_deck(paths.deck_path)
    panel_dir = NOTEBOOKS / "holdout" / "panel"
    out_dir = REPO_ROOT / "docs" / "phases" / "phase_01" / "offline" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    latest_path = out_dir / "phase1_holdout_summary_latest.json"

    all_rows: list[dict] = []
    for baseline in args.baselines:
        agent_path = AGENT_PATHS[baseline]
        if not agent_path.exists():
            raise FileNotFoundError(f"Missing agent file: {agent_path}")
        agent = load_baseline_agent(
            agent_path,
            our_deck,
            cg_parent=cg_parent,
            repo_root=paths.repo_root,
        )
        rows = run_holdout_suite(
            baseline_name=baseline,
            our_agent=agent,
            our_deck=our_deck,
            panel_dir=panel_dir,
            opponents=PHASE1_OPPONENTS,
            games=args.games,
        )
        all_rows.extend(rows)

    per_game = [r for r in all_rows if r.get("game_index") != "summary"]
    summaries = summarize_holdout(all_rows)

    if args.merge_latest and latest_path.exists():
        existing = json.loads(latest_path.read_text(encoding="utf-8"))
        summaries = merge_summaries(existing, summaries)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_csv(out_dir / f"phase1_holdout_games_{stamp}.csv", per_game)
    write_csv(out_dir / f"phase1_holdout_summary_{stamp}.csv", summaries)
    latest_path.write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote results to {out_dir}")
    for row in summaries:
        print(
            f"{row['baseline']:16} vs {row['opponent']:8} "
            f"win_rate={row['win_rate']:.3f} ({row['wins']}/{row['games']})"
        )


if __name__ == "__main__":
    main()
