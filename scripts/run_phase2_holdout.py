#!/usr/bin/env python3
"""Run Phase 2 holdout: Dragapult vs Starmie decks against the four archetypes."""

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

CANDIDATES = {
    "dragapult": {
        "deck": REPO_ROOT / "data" / "decks" / "dragapult.csv",
        "agent": NOTEBOOKS / "agents" / "main_baseline_a.py",
        "agent_label": "baseline_a_dragapult_policy",
    },
    "starmie": {
        "deck": REPO_ROOT / "data" / "decks" / "starmie.csv",
        "agent": NOTEBOOKS / "agents" / "main_starmie_heuristic.py",
        "agent_label": "starmie_heuristic",
    },
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2 deck-selection holdout")
    parser.add_argument("--games", type=int, default=40, help="Games per matchup (default: 40)")
    parser.add_argument(
        "--decks",
        nargs="+",
        default=["dragapult", "starmie"],
        choices=list(CANDIDATES.keys()),
    )
    args = parser.parse_args()

    paths = get_paths()
    paths.ensure_dirs()
    cg_parent = paths.cg_dir.parent if paths.cg_dir else None
    panel_dir = NOTEBOOKS / "holdout" / "panel"
    out_dir = REPO_ROOT / "docs" / "phases" / "phase_02" / "offline" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    for deck_name in args.decks:
        cfg = CANDIDATES[deck_name]
        our_deck = load_deck(cfg["deck"])
        agent = load_baseline_agent(
            cfg["agent"],
            our_deck,
            cg_parent=cg_parent,
            repo_root=paths.repo_root,
        )
        rows = run_holdout_suite(
            baseline_name=deck_name,
            our_agent=agent,
            our_deck=our_deck,
            panel_dir=panel_dir,
            opponents=PHASE1_OPPONENTS,
            games=args.games,
        )
        for row in rows:
            row["candidate_deck"] = deck_name
            row["agent"] = cfg["agent_label"]
        all_rows.extend(rows)

    per_game = [r for r in all_rows if r.get("game_index") != "summary"]
    summaries = summarize_holdout(all_rows)
    for row in summaries:
        name = row["baseline"]
        row["candidate_deck"] = name
        row["agent"] = CANDIDATES[name]["agent_label"]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_csv(out_dir / f"phase2_holdout_games_{stamp}.csv", per_game)
    write_csv(out_dir / f"phase2_holdout_summary_{stamp}.csv", summaries)
    (out_dir / "phase2_holdout_summary_latest.json").write_text(
        json.dumps(summaries, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote results to {out_dir}")
    for row in summaries:
        print(
            f"{row['candidate_deck']:10} vs {row['opponent']:8} "
            f"win_rate={row['win_rate']:.3f} ({row['wins']}/{row['games']}) "
            f"[{row['holdout_gate']}]"
        )


if __name__ == "__main__":
    main()
