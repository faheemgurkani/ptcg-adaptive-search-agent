#!/usr/bin/env python3
"""Analyze Phase 1 holdout results (Baseline A / B / merged)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
DOCS = REPO_ROOT / "docs"
OUTPUT_DIR = DOCS / "phases" / "phase_01" / "offline"
RESULTS_DIR = OUTPUT_DIR / "results"
SUMMARY_LATEST = RESULTS_DIR / "phase1_holdout_summary_latest.json"

LABELS = {
    "baseline_a": "A (no search)",
    "baseline_b": "B (+ search)",
    "baseline_merged": "Merged / C (+ search + adaptation)",
}


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run holdout first.")
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(rows: list[dict]) -> str:
    by_baseline: dict[str, list[dict]] = {}
    for row in rows:
        by_baseline.setdefault(row["baseline"], []).append(row)

    baselines = [b for b in ("baseline_a", "baseline_b", "baseline_merged") if b in by_baseline]
    opponents = sorted({r["opponent"] for r in rows})

    lines = ["# Phase 1 holdout analysis", ""]

    # Per-matchup table
    header = "| Opponent |"
    sep = "|----------|"
    for b in baselines:
        short = {"baseline_a": "A", "baseline_b": "B", "baseline_merged": "Merged"}.get(b, b)
        header += f" {short} |"
        sep += "-------:|"
    if "baseline_a" in by_baseline and "baseline_b" in by_baseline:
        header += " B − A |"
        sep += "------:|"
    if "baseline_b" in by_baseline and "baseline_merged" in by_baseline:
        header += " Merged − B |"
        sep += "----------:|"
    lines.extend(["## Win rate by matchup (40 games each)", "", header, sep])

    for opp in opponents:
        cells = [opp]
        rates: dict[str, float] = {}
        for b in baselines:
            r = next(x for x in rows if x["baseline"] == b and x["opponent"] == opp)
            rates[b] = float(r["win_rate"])
            cells.append(f"{rates[b]:.1%} ({r['wins']}/{r['games']})")
        if "baseline_a" in rates and "baseline_b" in rates:
            cells.append(f"{rates['baseline_b'] - rates['baseline_a']:+.1%}")
        if "baseline_b" in rates and "baseline_merged" in rates:
            cells.append(f"{rates['baseline_merged'] - rates['baseline_b']:+.1%}")
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("")

    def overall(name: str) -> tuple[float, int, int]:
        subset = by_baseline[name]
        wins = sum(int(r["wins"]) for r in subset)
        games = sum(int(r["games"]) for r in subset)
        return wins / games if games else 0.0, wins, games

    lines.append("## Overall (all opponents pooled)")
    lines.append("")
    pooled: dict[str, tuple[float, int, int]] = {}
    for b in baselines:
        pooled[b] = overall(b)
        rate, wins, games = pooled[b]
        lines.append(f"- **{LABELS.get(b, b)}:** {rate:.1%} ({wins}/{games})")
    if "baseline_a" in pooled and "baseline_b" in pooled:
        lines.append(f"- **Search net (B − A):** {pooled['baseline_b'][0] - pooled['baseline_a'][0]:+.1%}")
    if "baseline_b" in pooled and "baseline_merged" in pooled:
        lines.append(
            f"- **Adaptation net (Merged − B):** {pooled['baseline_merged'][0] - pooled['baseline_b'][0]:+.1%}"
        )
    if "baseline_a" in pooled and "baseline_merged" in pooled:
        lines.append(
            f"- **Full stack net (Merged − A):** {pooled['baseline_merged'][0] - pooled['baseline_a'][0]:+.1%}"
        )
    lines.append("")

    lines.append("## Holdout gates (≥52% per matchup)")
    lines.append("")
    for baseline in baselines:
        fails = [r["opponent"] for r in by_baseline[baseline] if r["holdout_gate"] == "holdout_fail"]
        label = LABELS.get(baseline, baseline)
        if fails:
            lines.append(f"- **{label}** fails vs: {', '.join(fails)}")
        else:
            lines.append(f"- **{label}** passes all matchups")
    lines.append("")

    lines.append("## What this means")
    lines.append("")
    lines.append(
        "- **Alakazam** uses a real rule-based opponent; low win rates there are the most meaningful signal."
    )
    lines.append(
        "- **Crustle / Spidops / Starmie** still use placeholder decks + random agent — treat those numbers as directional only."
    )
    if "baseline_merged" in by_baseline:
        lines.append(
            "- **Merged (Baseline C)** = search + opponent adaptation; offline KPIs below pair with pending ladder logs."
        )
        if "baseline_b" in pooled and "baseline_merged" in pooled:
            d = pooled["baseline_merged"][0] - pooled["baseline_b"][0]
            if d > 0.01:
                lines.append("- Adaptation on top of search improved pooled holdout vs Baseline B.")
            elif d < -0.01:
                lines.append("- Adaptation did not improve pooled holdout vs Baseline B in this panel.")
            else:
                lines.append("- Adaptation ≈ null vs Baseline B on this holdout panel (pooled).")
    lines.append("")

    lines.append("## Next steps")
    lines.append("")
    lines.append("1. ~~Baselines A/B offline + ladder~~ — see `docs/phases/phase_01/`.")
    lines.append("2. Record merged agent ladder ratings / replays when available (`online/KAGGLE_LOG.md`).")
    lines.append("3. **Optional:** replace placeholder opponent decks under `notebooks/holdout/panel/`.")
    lines.append("4. **Phase 2:** deck selection (Dragapult vs Starmie) using the same holdout harness.")
    lines.append("")
    lines.append("Phase 1 close-out: `docs/phases/phase_01/PHASE_01_COMPLETION.md`.")
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
