#!/usr/bin/env python3
"""Analyze Phase 3 ablation holdout → 2×2 matrix report (paper Table 1)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "phases" / "phase_03" / "offline"
RESULTS_DIR = OUTPUT_DIR / "results"
SUMMARY_LATEST = RESULTS_DIR / "phase3_holdout_summary_latest.json"

VERSION_ORDER = ("v1", "v2", "v3", "v4")
OPP_ORDER = ("alakazam", "crustle", "spidops", "starmie")

LABELS = {
    "v1": "V1 (policy only)",
    "v2": "V2 (+ search)",
    "v3": "V3 (+ adaptation)",
    "v4": "V4 (full)",
}


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run scripts/run_phase3_holdout.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def rate(rows: list[dict], version: str, opponent: str) -> tuple[float, dict]:
    row = next(r for r in rows if r["baseline"] == version and r["opponent"] == opponent)
    return float(row["win_rate"]), row


def pooled(rows: list[dict], version: str) -> tuple[float, int, int]:
    subset = [r for r in rows if r["baseline"] == version]
    wins = sum(int(r["wins"]) for r in subset)
    games = sum(int(r["games"]) for r in subset)
    return wins / games if games else 0.0, wins, games


def analyze(rows: list[dict]) -> str:
    versions = [v for v in VERSION_ORDER if any(r["baseline"] == v for r in rows)]

    lines = [
        "# Phase 3 — Ablation analysis (panel v2, committed Dragapult deck)",
        "",
        "## Ablation matrix (2×2)",
        "",
        "| Version | Search | Adaptation | Role |",
        "|---------|:------:|:----------:|------|",
        "| V1 | ✗ | ✗ | Pure Dragapult baseline |",
        "| V2 | ✓ | ✗ | Search contribution |",
        "| V3 | ✗ | ✓ | Adaptation contribution |",
        "| V4 | ✓ | ✓ | Full system |",
        "",
        "## Win rate by matchup (40 games each)",
        "",
    ]

    header = "| Opponent |" + "".join(f" {LABELS.get(v, v)} |" for v in versions)
    sep = "|----------|" + "".join("-------:|" for _ in versions)
    if "v1" in versions and "v2" in versions:
        header += " V2−V1 |"
        sep += "------:|"
    if "v1" in versions and "v3" in versions:
        header += " V3−V1 |"
        sep += "------:|"
    if "v2" in versions and "v4" in versions:
        header += " V4−V2 |"
        sep += "------:|"
    if "v3" in versions and "v4" in versions:
        header += " V4−V3 |"
        sep += "------:|"
    lines.extend([header, sep])

    for opp in OPP_ORDER:
        cells = [opp]
        wr: dict[str, float] = {}
        for v in versions:
            r, row = rate(rows, v, opp)
            wr[v] = r
            cells.append(f"{r:.1%} ({row['wins']}/{row['games']})")
        if "v1" in wr and "v2" in wr:
            cells.append(f"{wr['v2'] - wr['v1']:+.1%}")
        if "v1" in wr and "v3" in wr:
            cells.append(f"{wr['v3'] - wr['v1']:+.1%}")
        if "v2" in wr and "v4" in wr:
            cells.append(f"{wr['v4'] - wr['v2']:+.1%}")
        if "v3" in wr and "v4" in wr:
            cells.append(f"{wr['v4'] - wr['v3']:+.1%}")
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(["", "## Pooled (160 games per version)", ""])
    pool: dict[str, tuple[float, int, int]] = {}
    for v in versions:
        pool[v] = pooled(rows, v)
        rate_val, wins, games = pool[v]
        lines.append(f"- **{LABELS.get(v, v)}:** {rate_val:.1%} ({wins}/{games})")

    lines.append("")
    if "v1" in pool and "v2" in pool:
        lines.append(f"- **Search effect (V2 − V1):** {pool['v2'][0] - pool['v1'][0]:+.1%}")
    if "v1" in pool and "v3" in pool:
        lines.append(f"- **Adaptation effect (V3 − V1):** {pool['v3'][0] - pool['v1'][0]:+.1%}")
    if "v2" in pool and "v4" in pool:
        lines.append(f"- **Adaptation on search (V4 − V2):** {pool['v4'][0] - pool['v2'][0]:+.1%}")
    if "v3" in pool and "v4" in pool:
        lines.append(f"- **Search on adaptation (V4 − V3):** {pool['v4'][0] - pool['v3'][0]:+.1%}")
    if "v1" in pool and "v4" in pool:
        lines.append(f"- **Full stack (V4 − V1):** {pool['v4'][0] - pool['v1'][0]:+.1%}")

    lines.extend(["", "## Component attribution highlights", ""])

    if "v1" in versions and "v3" in versions:
        crustle_v1, _ = rate(rows, "v1", "crustle")
        crustle_v3, _ = rate(rows, "v3", "crustle")
        lines.append(
            f"- **Crustle/stall (adaptation hypothesis):** V3 − V1 = {crustle_v3 - crustle_v1:+.1%} "
            f"(V1 {crustle_v1:.1%} → V3 {crustle_v3:.1%})"
        )
    if "v1" in versions and "v2" in versions:
        ala_v1, _ = rate(rows, "v1", "alakazam")
        ala_v2, _ = rate(rows, "v2", "alakazam")
        lines.append(
            f"- **Alakazam (tactical/search signal):** V2 − V1 = {ala_v2 - ala_v1:+.1%} "
            f"(V1 {ala_v1:.1%} → V2 {ala_v2:.1%})"
        )

    lines.extend(["", "## Holdout gates (≥52% per matchup)", ""])
    for v in versions:
        fails = [r["opponent"] for r in rows if r["baseline"] == v and r["holdout_gate"] == "holdout_fail"]
        label = LABELS.get(v, v)
        if fails:
            lines.append(f"- **{label}** fails vs: {', '.join(fails)}")
        else:
            lines.append(f"- **{label}** passes all matchups")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Panel **v2** (upgraded Crustle/Spidops/Starmie decks); not comparable to Phase 1 panel v1 numbers.",
            "- Crustle/Spidops/Starmie opponents use random agents; Alakazam is rule-based.",
            "- Phase 1 early V4 (Merged C) was measured on panel v1; Phase 3 V4 re-runs on panel v2.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Phase 3 ablation holdout")
    parser.add_argument("--summary", type=Path, default=SUMMARY_LATEST)
    parser.add_argument("--write", type=Path, default=OUTPUT_DIR / "HOLDOUT_ANALYSIS.md")
    args = parser.parse_args()

    rows = load_summary(args.summary)
    report = analyze(rows)
    print(report)
    args.write.parent.mkdir(parents=True, exist_ok=True)
    args.write.write_text(report, encoding="utf-8")
    print(f"\nWrote {args.write}")


if __name__ == "__main__":
    main()
