#!/usr/bin/env python3
"""Phase 4 search-depth holdout: UCB1 candidates × time budget on V2 (search only)."""

from __future__ import annotations

import argparse
import csv
import json
import os
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
    reset_policy_counters,
    run_holdout_suite,
    summarize_holdout,
)

CANDIDATE_COUNTS = (4, 8, 12, 16)
TIME_BUDGETS = (0.5, 1.0, 1.5, 2.0)
DEFAULT_CANDIDATES = 8
DEFAULT_TIME = 1.5
V2_AGENT = NOTEBOOKS / "agents" / "main_baseline_b.py"


def cell_id(candidates: int, time_s: float) -> str:
    return f"c{candidates}_t{int(round(time_s * 1000))}"


def parse_cell(name: str) -> tuple[int, float]:
    # c8_t1500
    left, right = name.split("_t", 1)
    return int(left[1:]), int(right) / 1000.0


def crossed_cells() -> list[tuple[int, float]]:
    cells = [(DEFAULT_CANDIDATES, t) for t in TIME_BUDGETS]
    for c in CANDIDATE_COUNTS:
        if c != DEFAULT_CANDIDATES:
            cells.append((c, DEFAULT_TIME))
    return cells


def grid_cells() -> list[tuple[int, float]]:
    return [(c, t) for t in TIME_BUDGETS for c in CANDIDATE_COUNTS]


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


def annotate(row: dict, candidates: int, time_s: float) -> dict:
    row = dict(row)
    row["cell"] = cell_id(candidates, time_s)
    row["search_max_candidates"] = candidates
    row["search_time_budget_sec"] = time_s
    row["version"] = "v2"
    row["use_search"] = True
    row["use_adaptation"] = False
    row["committed_deck"] = "dragapult"
    row["panel_version"] = "v2"
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 4 search-depth holdout (panel v2, V2 only)")
    parser.add_argument("--games", type=int, default=40, help="Games per matchup (default: 40)")
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Full 4×4 candidates × time grid (16 cells). Default is two 1-D sweeps (7 cells).",
    )
    parser.add_argument(
        "--cells",
        nargs="+",
        default=None,
        help="Subset of cell ids (e.g. c8_t1500 c4_t1500). Default: crossed sweeps or --grid.",
    )
    parser.add_argument(
        "--merge-latest",
        action="store_true",
        help="Keep prior cells in phase4_holdout_summary_latest.json when re-running a subset.",
    )
    args = parser.parse_args()

    wanted: list[tuple[int, float]]
    if args.cells:
        wanted = [parse_cell(c) for c in args.cells]
    elif args.grid:
        wanted = grid_cells()
    else:
        wanted = crossed_cells()

    paths = get_paths()
    paths.ensure_dirs()
    cg_parent = paths.cg_dir.parent if paths.cg_dir else None
    deck_path = REPO_ROOT / "data" / "decks" / "dragapult.csv"
    if not deck_path.exists():
        deck_path = paths.deck_path
    our_deck = load_deck(deck_path)
    panel_dir = NOTEBOOKS / "holdout" / "panel"
    out_dir = REPO_ROOT / "docs" / "phases" / "phase_04" / "offline" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not V2_AGENT.exists():
        raise FileNotFoundError(f"Missing {V2_AGENT}. Run build_merged_agent.py --variant baseline_b")

    latest_path = out_dir / "phase4_holdout_summary_latest.json"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    all_rows: list[dict] = []
    kept_summaries: list[dict] = []
    running_ids = {cell_id(c, t) for c, t in wanted}
    if args.merge_latest and latest_path.exists():
        prior = json.loads(latest_path.read_text(encoding="utf-8"))
        kept_summaries = [r for r in prior if r.get("cell") not in running_ids]

    agent = load_baseline_agent(
        V2_AGENT,
        our_deck,
        cg_parent=cg_parent,
        repo_root=paths.repo_root,
    )
    mod = getattr(agent, "_module", None)

    def flush() -> list[dict]:
        per_game = [r for r in all_rows if r.get("game_index") != "summary"]
        summaries = kept_summaries + summarize_holdout(all_rows)
        write_csv(out_dir / f"phase4_holdout_games_{stamp}.csv", per_game)
        write_csv(out_dir / f"phase4_holdout_summary_{stamp}.csv", summaries)
        latest_path.write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")
        return summaries

    print(
        f"Phase 4 cells ({len(wanted)}): " + ", ".join(cell_id(c, t) for c, t in wanted),
        flush=True,
    )
    for candidates, time_s in wanted:
        cid = cell_id(candidates, time_s)
        os.environ["PTCG_SEARCH_TIME_BUDGET"] = str(time_s)
        os.environ["PTCG_SEARCH_MAX_CANDIDATES"] = str(candidates)
        if mod is not None:
            reset_policy_counters(mod)
        print(f"Starting {cid} (candidates={candidates}, time={time_s}s)", flush=True)
        rows = run_holdout_suite(
            baseline_name=cid,
            our_agent=agent,
            our_deck=our_deck,
            panel_dir=panel_dir,
            opponents=PHASE1_OPPONENTS,
            games=args.games,
        )
        for row in rows:
            all_rows.append(annotate(row, candidates, time_s))
        summaries = flush()
        print(f"Finished {cid}", flush=True)
        for row in summaries:
            if row.get("cell") != cid:
                continue
            print(
                f"{cid:12} vs {row['opponent']:8} "
                f"win_rate={row['win_rate']:.3f} ({row['wins']}/{row['games']}) "
                f"[{row['holdout_gate']}]",
                flush=True,
            )

    summaries = flush()
    print(f"Deck: {deck_path}")
    print(f"Panel: v2 — {panel_dir}")
    print(f"Wrote results to {out_dir}")
    for row in summaries:
        print(
            f"{row.get('cell', row['baseline']):12} vs {row['opponent']:8} "
            f"win_rate={row['win_rate']:.3f} ({row['wins']}/{row['games']}) "
            f"[{row['holdout_gate']}]"
        )


if __name__ == "__main__":
    main()
