#!/usr/bin/env python3
"""Analyze Phase 1 holdout results (Baseline A vs B)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

NOTEBOOKS = Path(__file__).resolve().parent
DOCS = NOTEBOOKS.parent / "docs"
OUTPUT_DIR = DOCS / "phases" / "phase_01" / "offline"
RESULTS_DIR = OUTPUT_DIR / "results"
SUMMARY_LATEST = RESULTS_DIR / "phase1_holdout_summary_latest.json"


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run PHASE_01_BASELINE_EVAL.ipynb first.")
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(rows: list[dict]) -> str:
    by_baseline: dict[str, list[dict]] = {}
    for row in rows:
        by_baseline.setdefault(row["baseline"], []).append(row)

    lines = ["# Phase 1 holdout analysis", ""]

    # Per-matchup table
    lines.append("## Win rate by matchup (40 games each)")
    lines.append("")
    lines.append("| Opponent | Baseline A | Baseline B | B − A | Search helped? |")
    lines.append("|----------|------------|------------|-------|----------------|")

    opponents = sorted({r["opponent"] for r in rows})
    deltas = []
    for opp in opponents:
        a = next(r for r in rows if r["baseline"] == "baseline_a" and r["opponent"] == opp)
        b = next(r for r in rows if r["baseline"] == "baseline_b" and r["opponent"] == opp)
        da = float(a["win_rate"])
        db = float(b["win_rate"])
        delta = db - da
        deltas.append(delta)
        helped = "yes" if delta > 0 else ("no" if delta < 0 else "tie")
        lines.append(
            f"| {opp} | {da:.1%} ({a['wins']}/{a['games']}) | "
            f"{db:.1%} ({b['wins']}/{b['games']}) | {delta:+.1%} | {helped} |"
        )

    lines.append("")

    # Overall
    def overall(name: str) -> tuple[float, int, int]:
        subset = by_baseline[name]
        wins = sum(int(r["wins"]) for r in subset)
        games = sum(int(r["games"]) for r in subset)
        return wins / games if games else 0.0, wins, games

    oa, wa, ga = overall("baseline_a")
    ob, wb, gb = overall("baseline_b")
    lines.append("## Overall (all opponents pooled)")
    lines.append("")
    lines.append(f"- **Baseline A:** {oa:.1%} ({wa}/{ga})")
    lines.append(f"- **Baseline B:** {ob:.1%} ({wb}/{gb})")
    lines.append(f"- **Search net change:** {ob - oa:+.1%}")
    lines.append("")

    # Gates
    lines.append("## Holdout gates (≥52% per matchup)")
    lines.append("")
    for baseline in ("baseline_a", "baseline_b"):
        fails = [r["opponent"] for r in by_baseline[baseline] if r["holdout_gate"] == "holdout_fail"]
        label = "A (no search)" if baseline == "baseline_a" else "B (+ search)"
        if fails:
            lines.append(f"- **{label}** fails vs: {', '.join(fails)}")
        else:
            lines.append(f"- **{label}** passes all matchups")
    lines.append("")

    # Interpretation
    lines.append("## What this means")
    lines.append("")
    lines.append(
        "- **Alakazam** uses a real rule-based opponent; low win rates there are the most meaningful signal."
    )
    lines.append(
        "- **Crustle / Spidops / Starmie** still use placeholder decks + random agent — treat those numbers as directional only."
    )
    if sum(d > 0 for d in deltas) > sum(d < 0 for d in deltas):
        lines.append("- Search wins more matchups than it loses in this run → keep search on for Phase 3 ablations.")
    else:
        lines.append("- Search is mixed or negative overall → still worth keeping for ablation story, but tune budget/candidates later.")
    lines.append("")

    lines.append("## Next steps")
    lines.append("")
    lines.append("1. **Kaggle:** submit Baseline A, then Baseline B; log ladder ratings in `docs/phases/phase_01/online/KAGGLE_LOG.md`.")
    lines.append("2. **Optional:** replace placeholder opponent decks under `notebooks/holdout/panel/`.")
    lines.append("3. **Phase 2:** deck selection (Dragapult vs Starmie) using the same holdout harness.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Phase 1 holdout output")
    parser.add_argument(
        "--summary",
        type=Path,
        default=SUMMARY_LATEST,
        help="Path to phase1_holdout_summary_latest.json",
    )
    parser.add_argument(
        "--write",
        type=Path,
        default=OUTPUT_DIR / "HOLDOUT_ANALYSIS.md",
        help="Write markdown report to this path",
    )
    args = parser.parse_args()

    rows = load_summary(args.summary)
    report = analyze(rows)
    print(report)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(report, encoding="utf-8")
        print(f"\nWrote {args.write}")


if __name__ == "__main__":
    main()
