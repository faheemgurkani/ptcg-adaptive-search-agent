#!/usr/bin/env python3
"""Analyze Phase 4 search-depth holdout → win-rate vs compute (paper Figure 2)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
PHASE4 = REPO_ROOT / "docs" / "phases" / "phase_04"
OUTPUT_DIR = PHASE4 / "offline"
RESULTS_DIR = OUTPUT_DIR / "results"
SUMMARY_LATEST = RESULTS_DIR / "phase4_holdout_summary_latest.json"
RESULTS_JSON = PHASE4 / "PHASE_04_RESULTS.json"

OPP_ORDER = ("alakazam", "crustle", "spidops", "starmie")
# Phase 3 V1 / V2 anchors (panel v2, repaired choose(); not mixed into the sweep)
PHASE3_V1_POOLED = 0.90
PHASE3_V2_POOLED = 0.3625
PHASE3_V2_TIME = 0.3
PHASE3_V2_CAND = 8
KNEE_TOLERANCE_PP = 2.0


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run scripts/run_phase4_holdout.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def cell_meta(row: dict) -> tuple[str, int, float]:
    cell = str(row.get("cell") or row["baseline"])
    cand = int(row["search_max_candidates"])
    time_s = float(row["search_time_budget_sec"])
    return cell, cand, time_s


def group_cells(rows: list[dict]) -> dict[str, dict]:
    cells: dict[str, dict] = {}
    for row in rows:
        cell, cand, time_s = cell_meta(row)
        bucket = cells.setdefault(
            cell,
            {
                "cell": cell,
                "search_max_candidates": cand,
                "search_time_budget_sec": time_s,
                "matchups": {},
                "wins": 0,
                "games": 0,
                "choose_ok": int(row.get("choose_ok") or 0),
                "choose_fail": int(row.get("choose_fail") or 0),
                "search_ok": int(row.get("search_ok") or 0),
                "search_fail": int(row.get("search_fail") or 0),
            },
        )
        opp = row["opponent"]
        bucket["matchups"][opp] = {
            "win_rate": float(row["win_rate"]),
            "wins": int(row["wins"]),
            "losses": int(row["losses"]),
            "ties": int(row.get("ties") or 0),
            "games": int(row["games"]),
            "holdout_gate": row.get("holdout_gate"),
        }
        bucket["wins"] += int(row["wins"])
        bucket["games"] += int(row["games"])
    for bucket in cells.values():
        g = bucket["games"]
        bucket["pooled"] = bucket["wins"] / g if g else 0.0
        bucket["equal_weight"] = (
            sum(bucket["matchups"][o]["win_rate"] for o in OPP_ORDER if o in bucket["matchups"])
            / max(1, sum(1 for o in OPP_ORDER if o in bucket["matchups"]))
        )
    return cells


def knee(points: list[tuple[float, float]], *, increasing_x: bool = True) -> dict:
    """Smallest x whose WR is within KNEE_TOLERANCE_PP of the best WR on the curve."""
    if not points:
        return {"x": None, "win_rate": None, "note": "no points"}
    ordered = sorted(points, key=lambda p: p[0])
    best_wr = max(p[1] for p in ordered)
    threshold = best_wr - KNEE_TOLERANCE_PP / 100.0
    chosen = None
    for x, wr in ordered:
        if wr >= threshold:
            chosen = (x, wr)
            break
    if chosen is None:
        chosen = ordered[0]
    first, last = ordered[0], ordered[-1]
    monotone_down = all(ordered[i][1] >= ordered[i + 1][1] - 1e-9 for i in range(len(ordered) - 1))
    monotone_up = all(ordered[i][1] <= ordered[i + 1][1] + 1e-9 for i in range(len(ordered) - 1))
    note = "additional search never helps (best at lowest budget)" if monotone_down and chosen == first else (
        "win rate still rising at max budget" if monotone_up and chosen == last else
        f"within {KNEE_TOLERANCE_PP:.0f} pp of best"
    )
    return {
        "x": chosen[0],
        "win_rate": chosen[1],
        "best_win_rate": best_wr,
        "best_x": max(ordered, key=lambda p: p[1])[0],
        "note": note,
        "monotone_down": monotone_down,
        "monotone_up": monotone_up,
    }


def build_payload(rows: list[dict]) -> dict:
    cells = group_cells(rows)
    time_curve = sorted(
        [
            (v["search_time_budget_sec"], v["pooled"], v["cell"])
            for v in cells.values()
            if v["search_max_candidates"] == 8
        ]
    )
    cand_curve = sorted(
        [
            (v["search_max_candidates"], v["pooled"], v["cell"])
            for v in cells.values()
            if abs(v["search_time_budget_sec"] - 1.5) < 1e-9
        ]
    )
    time_knee = knee([(t, wr) for t, wr, _ in time_curve])
    cand_knee = knee([(float(c), wr) for c, wr, _ in cand_curve])
    best = max(cells.values(), key=lambda v: v["pooled"]) if cells else None
    sample = next(iter(cells.values()), None)
    gpm = None
    if sample and sample["matchups"]:
        gpm = next(iter(sample["matchups"].values()))["games"]
    status = "pending"
    if cells:
        status = "complete" if len(cells) >= 7 else "in_progress"
    return {
        "phase": 4,
        "status": status,
        "protocol": {
            "agent": "V2 (search only, no adaptation)",
            "agent_path": "notebooks/agents/main_baseline_b.py",
            "committed_deck": "dragapult",
            "panel_version": "v2",
            "games_per_matchup": gpm,
            "candidate_counts": sorted({v["search_max_candidates"] for v in cells.values()}),
            "time_budgets_sec": sorted({v["search_time_budget_sec"] for v in cells.values()}),
            "n_cells": len(cells),
            "knee_tolerance_pp": KNEE_TOLERANCE_PP,
            "phase3_reference": {
                "v1_pooled": PHASE3_V1_POOLED,
                "v2_pooled": PHASE3_V2_POOLED,
                "v2_time_sec": PHASE3_V2_TIME,
                "v2_candidates": PHASE3_V2_CAND,
            },
        },
        "cells": cells,
        "curves": {
            "time_at_8_candidates": [
                {"time_sec": t, "pooled": wr, "cell": cid} for t, wr, cid in time_curve
            ],
            "candidates_at_1_5s": [
                {"candidates": int(c), "pooled": wr, "cell": cid} for c, wr, cid in cand_curve
            ],
        },
        "knee": {
            "time_sec": time_knee,
            "candidates": cand_knee,
        },
        "best_cell": None
        if best is None
        else {
            "cell": best["cell"],
            "pooled": best["pooled"],
            "search_max_candidates": best["search_max_candidates"],
            "search_time_budget_sec": best["search_time_budget_sec"],
            "vs_v1_pp": (best["pooled"] - PHASE3_V1_POOLED) * 100,
        },
        "findings": [],
    }


def findings(payload: dict) -> list[str]:
    out: list[str] = []
    best = payload.get("best_cell")
    if best:
        out.append(
            f"Best search cell {best['cell']} at {best['pooled']:.1%} pooled "
            f"({best['vs_v1_pp']:+.1f} pp vs Phase 3 V1 {PHASE3_V1_POOLED:.1%})."
        )
    tk = payload["knee"]["time_sec"]
    ck = payload["knee"]["candidates"]
    if tk.get("x") is not None:
        out.append(f"Time-budget knee (8 candidates): {tk['x']} s — {tk['note']}.")
    if ck.get("x") is not None:
        out.append(f"Candidate-count knee (1.5 s): {int(ck['x'])} — {ck['note']}.")
    if best and best["pooled"] < PHASE3_V1_POOLED - 0.05:
        out.append("No searched configuration approaches the no-search V1 baseline.")
    return out


def write_analysis(payload: dict) -> str:
    lines = [
        "# Phase 4 holdout analysis — search depth",
        "",
        "Panel **v2**, committed **Dragapult**, agent **V2** (UCB1 on, adaptation off).",
        "Paired seeds (`md5(opponent:game_idx)`). `choose()` must succeed.",
        "",
        "## Cells",
        "",
        "| Cell | Candidates | Time (s) | Alakazam | Crustle | Spidops | Starmie | **Pooled** | Record |",
        "|------|----------:|---------:|---------:|--------:|--------:|--------:|-----------:|--------|",
    ]
    cells = sorted(
        payload["cells"].values(),
        key=lambda v: (v["search_time_budget_sec"], v["search_max_candidates"]),
    )
    for v in cells:
        mu = v["matchups"]
        def pct(o: str) -> str:
            return f"{mu[o]['win_rate']:.1%}" if o in mu else "—"
        lines.append(
            f"| `{v['cell']}` | {v['search_max_candidates']} | {v['search_time_budget_sec']:.1f} | "
            f"{pct('alakazam')} | {pct('crustle')} | {pct('spidops')} | {pct('starmie')} | "
            f"**{v['pooled']:.1%}** | {v['wins']}/{v['games']} |"
        )
    lines.extend(
        [
            "",
            f"Phase 3 anchors (not re-run): V1 **{PHASE3_V1_POOLED:.1%}**; "
            f"V2 at 0.3 s / 8 candidates **{PHASE3_V2_POOLED:.1%}**.",
            "",
            "## Time curve (8 candidates)",
            "",
            "| Time (s) | Pooled |",
            "|---------:|-------:|",
        ]
    )
    for pt in payload["curves"]["time_at_8_candidates"]:
        lines.append(f"| {pt['time_sec']:.1f} | {pt['pooled']:.1%} |")
    tk = payload["knee"]["time_sec"]
    if tk.get("x") is not None:
        lines.append(f"\n**Knee:** {tk['x']} s ({tk['note']}).")
    lines.extend(
        [
            "",
            "## Candidate curve (1.5 s)",
            "",
            "| Candidates | Pooled |",
            "|-----------:|-------:|",
        ]
    )
    for pt in payload["curves"]["candidates_at_1_5s"]:
        lines.append(f"| {pt['candidates']} | {pt['pooled']:.1%} |")
    ck = payload["knee"]["candidates"]
    if ck.get("x") is not None:
        lines.append(f"\n**Knee:** {int(ck['x'])} candidates ({ck['note']}).")
    lines.extend(["", "## Findings", ""])
    for item in payload["findings"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Paper",
            "",
            "This is Figure 2 (win rate vs compute). Do not mix with Phase 3 V2 0.3 s except as a labeled reference.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_log(payload: dict) -> str:
    proto = payload["protocol"]
    return "\n".join(
        [
            "# Phase 4 holdout log",
            "",
            f"**Status:** {payload['status']}",
            "",
            "| Item | Value |",
            "|------|-------|",
            f"| Agent | {proto['agent']} |",
            f"| Deck | {proto['committed_deck']} |",
            f"| Panel | {proto['panel_version']} |",
            f"| Games / matchup | {proto['games_per_matchup']} |",
            f"| Cells | {proto['n_cells']} |",
            f"| Candidates | {proto['candidate_counts']} |",
            f"| Time budgets (s) | {proto['time_budgets_sec']} |",
            "| Seeds | paired `md5(opponent:game_idx)` |",
            "",
            "CLI: `python scripts/run_phase4_holdout.py --games 40`",
            "Full grid: add `--grid` (16 cells).",
            "Analyze: `python scripts/analyze_phase4_results.py`",
            "",
        ]
    ) + "\n"


def write_readme(payload: dict) -> str:
    best = payload.get("best_cell")
    best_line = (
        f"Best cell `{best['cell']}` at **{best['pooled']:.1%}** pooled."
        if best
        else "Results pending."
    )
    return "\n".join(
        [
            "# Phase 4 — Search depth analysis",
            "",
            f"**Status: {payload['status'].upper()}** — see [`PHASE_04_RESULTS.json`](PHASE_04_RESULTS.json)",
            "",
            "**Goal:** How much UCB1 search depth matters under a wall-clock budget. Paper **Figure 2**.",
            "",
            "| Track | Doc | Results |",
            "|-------|-----|---------|",
            "| **Offline** V2 sweep | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) · [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |",
            "",
            "## Protocol",
            "",
            "- Agent: **V2** (search on, adaptation off) + committed Dragapult + panel v2.",
            "- Candidates: 4, 8, 12, 16. Time: 0.5, 1.0, 1.5, 2.0 s.",
            "- Default run: two 1-D sweeps (8 candidates × all times; 1.5 s × all candidate counts) = 7 cells × 160 games.",
            "- `--grid` runs the full 4×4 (16 cells).",
            "",
            "## Result",
            "",
            best_line,
            "",
            "## Commands",
            "",
            "```bash",
            ".venv/bin/python scripts/build_merged_agent.py --variant baseline_b",
            ".venv/bin/python scripts/run_phase4_holdout.py --games 40",
            ".venv/bin/python scripts/analyze_phase4_results.py",
            "python docs/research_paper_writeup/generate_phase4_figures.py",
            "```",
            "",
        ]
    ) + "\n"


def write_completion(payload: dict) -> str:
    return "\n".join(
        [
            "# Phase 4 completion",
            "",
            f"**Status:** {payload['status']}",
            "",
            "Search-depth sweep on repaired V2 (panel v2, Dragapult).",
            "",
            *([f"- {x}" for x in payload["findings"]] or ["- Sweep in progress."]),
            "",
            "Artifacts: `PHASE_04_RESULTS.json`, `offline/HOLDOUT_ANALYSIS.md`, `offline/results/`.",
            "",
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Phase 4 search-depth holdout")
    parser.add_argument("--summary", type=Path, default=SUMMARY_LATEST)
    args = parser.parse_args()
    rows = load_summary(args.summary)
    payload = build_payload(rows)
    payload["findings"] = findings(payload)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "HOLDOUT_ANALYSIS.md").write_text(write_analysis(payload), encoding="utf-8")
    (OUTPUT_DIR / "HOLDOUT_LOG.md").write_text(write_log(payload), encoding="utf-8")
    (PHASE4 / "README.md").write_text(write_readme(payload), encoding="utf-8")
    (PHASE4 / "PHASE_04_COMPLETION.md").write_text(write_completion(payload), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"cells={payload['protocol']['n_cells']} best={payload.get('best_cell')}")


if __name__ == "__main__":
    main()
