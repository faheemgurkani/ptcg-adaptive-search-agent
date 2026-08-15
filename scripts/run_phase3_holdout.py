#!/usr/bin/env python3
"""Run Phase 3 ablation holdout: V1–V4 on panel v2 with committed Dragapult deck."""

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

# Phase 3 ablation matrix (2×2: search × adaptation)
ABLATION_VARIANTS = {
    "v1": {
        "baseline_key": "baseline_a",
        "agent": NOTEBOOKS / "agents" / "main_baseline_a.py",
        "search": False,
        "adaptation": False,
        "label": "V1 — pure Dragapult policy",
    },
    "v2": {
        "baseline_key": "baseline_b",
        "agent": NOTEBOOKS / "agents" / "main_baseline_b.py",
        "search": True,
        "adaptation": False,
        "label": "V2 — UCB1 search only",
    },
    "v3": {
        "baseline_key": "baseline_v3",
        "agent": NOTEBOOKS / "agents" / "main_baseline_v3.py",
        "search": False,
        "adaptation": True,
        "label": "V3 — adaptation only",
    },
    "v4": {
        "baseline_key": "baseline_merged",
        "agent": NOTEBOOKS / "agents" / "main_baseline_merged.py",
        "search": True,
        "adaptation": True,
        "label": "V4 — full system",
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
    parser = argparse.ArgumentParser(description="Phase 3 ablation holdout (panel v2)")
    parser.add_argument("--games", type=int, default=40, help="Games per matchup (default: 40)")
    parser.add_argument(
        "--variants",
        nargs="+",
        default=list(ABLATION_VARIANTS.keys()),
        choices=list(ABLATION_VARIANTS.keys()),
    )
    args = parser.parse_args()

    paths = get_paths()
    paths.ensure_dirs()
    cg_parent = paths.cg_dir.parent if paths.cg_dir else None
    deck_path = REPO_ROOT / "data" / "decks" / "dragapult.csv"
    if not deck_path.exists():
        deck_path = paths.deck_path
    our_deck = load_deck(deck_path)
    panel_dir = NOTEBOOKS / "holdout" / "panel"
    out_dir = REPO_ROOT / "docs" / "phases" / "phase_03" / "offline" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    for version in args.variants:
        cfg = ABLATION_VARIANTS[version]
        agent_path = cfg["agent"]
        if not agent_path.exists():
            raise FileNotFoundError(f"Missing agent: {agent_path}. Run build_merged_agent.py --variant {cfg['baseline_key']}")
        agent = load_baseline_agent(
            agent_path,
            our_deck,
            cg_parent=cg_parent,
            repo_root=paths.repo_root,
        )
        rows = run_holdout_suite(
            baseline_name=version,
            our_agent=agent,
            our_deck=our_deck,
            panel_dir=panel_dir,
            opponents=PHASE1_OPPONENTS,
            games=args.games,
        )
        for row in rows:
            row["version"] = version
            row["baseline_key"] = cfg["baseline_key"]
            row["use_search"] = cfg["search"]
            row["use_adaptation"] = cfg["adaptation"]
            row["committed_deck"] = "dragapult"
            row["panel_version"] = "v2"
        all_rows.extend(rows)

    per_game = [r for r in all_rows if r.get("game_index") != "summary"]
    summaries = summarize_holdout(all_rows)
    for row in summaries:
        version = row["baseline"]
        cfg = ABLATION_VARIANTS[version]
        row["version"] = version
        row["baseline_key"] = cfg["baseline_key"]
        row["use_search"] = cfg["search"]
        row["use_adaptation"] = cfg["adaptation"]
        row["committed_deck"] = "dragapult"
        row["panel_version"] = "v2"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_csv(out_dir / f"phase3_holdout_games_{stamp}.csv", per_game)
    write_csv(out_dir / f"phase3_holdout_summary_{stamp}.csv", summaries)
    (out_dir / "phase3_holdout_summary_latest.json").write_text(
        json.dumps(summaries, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Deck: {deck_path}")
    print(f"Panel: v2 — {panel_dir}")
    print(f"Wrote results to {out_dir}")
    for row in summaries:
        print(
            f"{row['version']:3} vs {row['opponent']:8} "
            f"win_rate={row['win_rate']:.3f} ({row['wins']}/{row['games']}) "
            f"[{row['holdout_gate']}]"
        )


if __name__ == "__main__":
    main()
