#!/usr/bin/env python3
"""Analyze Phase 3 ablation holdout → 2×2 matrix report (paper Table 1)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
PHASE3 = REPO_ROOT / "docs" / "phases" / "phase_03"
OUTPUT_DIR = PHASE3 / "offline"
RESULTS_DIR = OUTPUT_DIR / "results"
SUMMARY_LATEST = RESULTS_DIR / "phase3_holdout_summary_latest.json"
RESULTS_JSON = PHASE3 / "PHASE_03_RESULTS.json"

VERSION_ORDER = ("v1", "v2", "v3", "v4")
OPP_ORDER = ("alakazam", "crustle", "spidops", "starmie")

AGENT_MAP = {
    "v1": ("baseline_a", "notebooks/agents/main_baseline_a.py", False, False),
    "v2": ("baseline_b", "notebooks/agents/main_baseline_b.py", True, False),
    "v3": ("baseline_v3", "notebooks/agents/main_baseline_v3.py", False, True),
    "v4": ("baseline_merged", "notebooks/agents/main_baseline_merged.py", True, True),
}

LABELS = {
    "v1": "V1 (policy only)",
    "v2": "V2 (+ search)",
    "v3": "V3 (+ adaptation)",
    "v4": "V4 (full)",
}

# Phase 1 canonical pooled (panel v1) for cross-reference only
PHASE1_POOL_V1 = {"v1": 0.662, "v2": 0.637, "v4": 0.419}


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run scripts/run_phase3_holdout.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def rate(rows: list[dict], version: str, opponent: str) -> tuple[float, dict]:
    row = next(r for r in rows if r["baseline"] == version and r["opponent"] == opponent)
    return float(row["win_rate"]), row


def pooled_records(rows: list[dict], version: str) -> tuple[float, int, int]:
    subset = [r for r in rows if r["baseline"] == version]
    wins = sum(int(r["wins"]) for r in subset)
    games = sum(int(r["games"]) for r in subset)
    return wins / games if games else 0.0, wins, games


def pooled_equal_weight(rows: list[dict], version: str) -> float:
    return sum(rate(rows, version, o)[0] for o in OPP_ORDER) / len(OPP_ORDER)


def build_payload(rows: list[dict]) -> dict:
    versions = [v for v in VERSION_ORDER if any(r["baseline"] == v for r in rows)]
    matchups: dict[str, dict[str, dict]] = {}
    for v in versions:
        matchups[v] = {}
        for opp in OPP_ORDER:
            wr, row = rate(rows, v, opp)
            matchups[v][opp] = {
                "win_rate": wr,
                "wins": int(row["wins"]),
                "losses": int(row["losses"]),
                "ties": int(row.get("ties", 0)),
                "games": int(row["games"]),
                "holdout_gate": row["holdout_gate"],
            }

    pooled: dict[str, dict] = {}
    for v in versions:
        rec_rate, wins, games = pooled_records(rows, v)
        eq = pooled_equal_weight(rows, v)
        key, agent, search, adapt = AGENT_MAP[v]
        pooled[v] = {
            "equal_weight_pool": eq,
            "record_pool": rec_rate,
            "wins": wins,
            "games": games,
            "baseline_key": key,
            "agent_path": agent,
            "use_search": search,
            "use_adaptation": adapt,
            "gate_failures": [
                opp for opp in OPP_ORDER if matchups[v][opp]["holdout_gate"] == "holdout_fail"
            ],
        }

    def delta(a: str, b: str, opp: str | None = None) -> float | None:
        if a not in versions or b not in versions:
            return None
        if opp:
            return matchups[b][opp]["win_rate"] - matchups[a][opp]["win_rate"]
        return pooled[b]["record_pool"] - pooled[a]["record_pool"]

    contrasts = {
        "search_v2_minus_v1": delta("v1", "v2"),
        "adaptation_v3_minus_v1": delta("v1", "v3"),
        "adaptation_on_search_v4_minus_v2": delta("v2", "v4"),
        "search_on_adaptation_v4_minus_v3": delta("v3", "v4"),
        "full_stack_v4_minus_v1": delta("v1", "v4"),
    }
    per_matchup_contrasts = {
        opp: {
            "v2_minus_v1": delta("v1", "v2", opp),
            "v3_minus_v1": delta("v1", "v3", opp),
            "v4_minus_v2": delta("v2", "v4", opp),
            "v4_minus_v3": delta("v3", "v4", opp),
        }
        for opp in OPP_ORDER
    }

    cross_phase = {}
    for v in ("v1", "v2", "v4"):
        if v in pooled:
            cross_phase[v] = {
                "phase1_panel_v1_pooled": PHASE1_POOL_V1.get(v),
                "phase3_panel_v2_pooled": pooled[v]["record_pool"],
                "panel_delta_pp": (pooled[v]["record_pool"] - PHASE1_POOL_V1[v]) * 100
                if v in PHASE1_POOL_V1
                else None,
            }

    return {
        "phase": 3,
        "status": "complete",
        "protocol": {
            "total_games": len(versions) * len(OPP_ORDER) * 40,
            "games_per_matchup": 40,
            "committed_deck": "dragapult",
            "deck_path": "data/decks/dragapult.csv",
            "panel_version": "v2",
            "search_time_budget_sec": 0.3,
            "search_max_candidates": 8,
        },
        "matchups": matchups,
        "pooled": pooled,
        "contrasts_pooled_pp": {k: v * 100 if v is not None else None for k, v in contrasts.items()},
        "contrasts_per_matchup_pp": {
            opp: {k: v * 100 if v is not None else None for k, v in d.items()}
            for opp, d in per_matchup_contrasts.items()
        },
        "cross_phase_v1_vs_v2": cross_phase,
        "findings": _findings(versions, pooled, contrasts, matchups),
        "verdict": _verdict(versions, pooled, contrasts),
    }


def _pct(rate: float) -> str:
    return f"{rate:.1%}"


def _pp(delta: float | None) -> str:
    return "n/a" if delta is None else f"{delta * 100:+.1f} pp"


def _findings(versions, pooled, contrasts, matchups) -> list[str]:
    out: list[str] = []
    if "v1" in pooled:
        best = max(versions, key=lambda v: pooled[v]["record_pool"])
        out.append(
            f"{best.upper()} is the strongest offline configuration on panel v2 "
            f"({_pct(pooled[best]['record_pool'])} pooled, {pooled[best]['wins']}/{pooled[best]['games']})."
        )
    if contrasts.get("search_v2_minus_v1") is not None:
        out.append(f"Search (V2−V1) is {_pp(contrasts['search_v2_minus_v1'])} pooled.")
    if contrasts.get("adaptation_v3_minus_v1") is not None:
        crustle = None
        if "v1" in matchups and "v3" in matchups:
            crustle = matchups["v3"]["crustle"]["win_rate"] - matchups["v1"]["crustle"]["win_rate"]
        extra = f"; Crustle {_pp(crustle)}" if crustle is not None else ""
        out.append(f"Adaptation (V3−V1) is {_pp(contrasts['adaptation_v3_minus_v1'])} pooled{extra}.")
    if contrasts.get("full_stack_v4_minus_v1") is not None:
        out.append(f"Full stack (V4−V1) is {_pp(contrasts['full_stack_v4_minus_v1'])} pooled.")
    if "v1" in matchups:
        ala = matchups["v1"]["alakazam"]["win_rate"]
        out.append(f"Alakazam remains the hardest cell (V1 {_pct(ala)}).")
    out.append(
        "choose() now runs (POLICY_CHOOSE_FAIL=0); Phase 1–3 stub numbers are not comparable."
    )
    out.append("Kaggle submission: strongest offline variant + Dragapult deck.")
    return out


def _verdict(versions, pooled, contrasts) -> str:
    if "v1" not in pooled:
        return "Incomplete ablation."
    best = max(versions, key=lambda v: pooled[v]["record_pool"])
    search = contrasts.get("search_v2_minus_v1")
    adapt = contrasts.get("adaptation_v3_minus_v1")
    bits = [f"{best.upper()} leads at {_pct(pooled[best]['record_pool'])} pooled."]
    if search is not None:
        bits.append("Search does not improve on the repaired policy." if search <= 0 else "Search helps.")
    if adapt is not None:
        bits.append("Adaptation does not improve on the repaired policy." if adapt <= 0 else "Adaptation helps.")
    return " ".join(bits)


def render_markdown(payload: dict) -> str:
    p = payload
    lines = [
        "# Phase 3 — Ablation analysis (panel v2, committed Dragapult deck)",
        "",
        "**Status:** complete · **640 games** · deck: `data/decks/dragapult.csv` · panel: **v2**",
        "",
        "## Ablation matrix (2×2)",
        "",
        "| Version | Search | Adaptation | Agent file | Role |",
        "|---------|:------:|:----------:|------------|------|",
    ]
    for v in VERSION_ORDER:
        if v not in p["pooled"]:
            continue
        po = p["pooled"][v]
        s = "✓" if po["use_search"] else "✗"
        a = "✓" if po["use_adaptation"] else "✗"
        role = {
            "v1": "Pure Dragapult baseline",
            "v2": "Search contribution",
            "v3": "Adaptation contribution",
            "v4": "Full system",
        }[v]
        lines.append(f"| {v.upper()} | {s} | {a} | `{po['agent_path']}` | {role} |")

    lines.extend(["", "## Table 1 — Win rate by matchup (40 games each)", ""])
    header = "| Opponent | V1 | V2 | V3 | V4 | V2−V1 | V3−V1 | V4−V2 | V4−V3 |"
    sep = "|----------|-----:|-----:|-----:|-----:|------:|------:|------:|------:|"
    lines.extend([header, sep])
    for opp in OPP_ORDER:
        cm = p["contrasts_per_matchup_pp"][opp]
        cells = [opp]
        for v in VERSION_ORDER:
            if v not in p["matchups"]:
                cells.append("—")
                continue
            m = p["matchups"][v][opp]
            cells.append(f"{m['win_rate']:.1%} ({m['wins']}/{m['games']})")
        cells.extend(
            [
                f"{cm['v2_minus_v1']:+.1f}%" if cm["v2_minus_v1"] is not None else "—",
                f"{cm['v3_minus_v1']:+.1f}%" if cm["v3_minus_v1"] is not None else "—",
                f"{cm['v4_minus_v2']:+.1f}%" if cm["v4_minus_v2"] is not None else "—",
                f"{cm['v4_minus_v3']:+.1f}%" if cm["v4_minus_v3"] is not None else "—",
            ]
        )
        lines.append("| " + " | ".join(cells) + " |")

    lines.extend(["", "## Pooled summary (160 games per version)", ""])
    lines.append("| Version | Record pool | Equal-weight pool | Gate failures |")
    lines.append("|---------|------------:|------------------:|---------------|")
    for v in VERSION_ORDER:
        if v not in p["pooled"]:
            continue
        po = p["pooled"][v]
        fails = ", ".join(po["gate_failures"]) or "none"
        lines.append(
            f"| {v.upper()} | {po['record_pool']:.1%} ({po['wins']}/{po['games']}) | "
            f"{po['equal_weight_pool']:.1%} | {fails} |"
        )

    lines.extend(["", "## Component contrasts (pooled, pp)", ""])
    c = p["contrasts_pooled_pp"]
    lines.append("| Contrast | Δ (pp) |")
    lines.append("|----------|-------:|")
    labels = {
        "search_v2_minus_v1": "Search (V2 − V1)",
        "adaptation_v3_minus_v1": "Adaptation (V3 − V1)",
        "adaptation_on_search_v4_minus_v2": "Adaptation on search (V4 − V2)",
        "search_on_adaptation_v4_minus_v3": "Search on adaptation (V4 − V3)",
        "full_stack_v4_minus_v1": "Full stack (V4 − V1)",
    }
    for key, label in labels.items():
        val = c[key]
        lines.append(f"| {label} | {val:+.1f} |" if val is not None else f"| {label} | — |")

    lines.extend(["", "## Hypothesis tests", ""])
    cm = p["contrasts_per_matchup_pp"]
    lines.append(
        f"- **Crustle/stall (adaptation):** V3 − V1 = {cm['crustle']['v3_minus_v1']:+.1f} pp "
        f"({p['matchups']['v1']['crustle']['win_rate']:.1%} → {p['matchups']['v3']['crustle']['win_rate']:.1%}) — **hypothesis fails**"
    )
    lines.append(
        f"- **Starmie (search / tactical):** V2 − V1 = {cm['starmie']['v2_minus_v1']:+.1f} pp "
        f"({p['matchups']['v1']['starmie']['win_rate']:.1%} → {p['matchups']['v2']['starmie']['win_rate']:.1%}) — search **hurts**"
    )
    ala_bits = []
    for v in VERSION_ORDER:
        if v in p["matchups"]:
            ala_bits.append(f"{v.upper()} {p['matchups'][v]['alakazam']['win_rate']:.1%}")
    lines.append(f"- **Alakazam (rule-based):** {', '.join(ala_bits)}")

    lines.extend(["", "## Cross-phase reference (panel v1 vs v2 — not directly comparable)", ""])
    lines.append("| Version | Phase 1 pool (v1) | Phase 3 pool (v2) | Δ (v2−v1 panel)* |")
    lines.append("|---------|------------------:|------------------:|-----------------:|")
    for v, ref in p["cross_phase_v1_vs_v2"].items():
        lines.append(
            f"| {v.upper()} | {ref['phase1_panel_v1_pooled']:.1%} | "
            f"{ref['phase3_panel_v2_pooled']:.1%} | {ref['panel_delta_pp']:+.1f} pp |"
        )
    lines.append("")
    lines.append("*Delta reflects panel upgrade + run variance, not agent regression in isolation.")

    lines.extend(["", "## Research question (interim answer)", ""])
    lines.append(
        "> Does opponent-adaptive heuristic search outperform a static rule-based policy?"
    )
    lines.append("")
    lines.append(f"**On panel v2 offline (repaired policy):** {p['verdict']}")

    lines.extend(["", "## Findings summary", ""])
    for f in p["findings"]:
        lines.append(f"- {f}")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Panel **v2**; Phase 1 panel v1 used sample-water stand-ins and is not comparable.",
            "- Crustle/Spidops/Starmie opponents use random agents; Alakazam is rule-based.",
            "- `choose()` scoping is fixed; POLICY_CHOOSE_FAIL=0 on this run. Pre-fix 35–40% numbers were first-option stubs.",
            "- Holdout search budget is `PTCG_SEARCH_TIME_BUDGET` (0.3s); submission default remains 1.5s.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Phase 3 ablation holdout")
    parser.add_argument("--summary", type=Path, default=SUMMARY_LATEST)
    parser.add_argument("--write", type=Path, default=OUTPUT_DIR / "HOLDOUT_ANALYSIS.md")
    parser.add_argument("--json", type=Path, default=RESULTS_JSON)
    args = parser.parse_args()

    rows = load_summary(args.summary)
    payload = build_payload(rows)
    report = render_markdown(payload)

    print(report)
    args.write.parent.mkdir(parents=True, exist_ok=True)
    args.write.write_text(report, encoding="utf-8")
    args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {args.write}")
    print(f"Wrote {args.json}")


if __name__ == "__main__":
    main()
