#!/usr/bin/env python3
"""Analyze Phase 2 holdout + meta snapshot → deck commitment decision."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
DOCS = REPO_ROOT / "docs" / "phases" / "phase_02"
OFFLINE = DOCS / "offline"
RESULTS = OFFLINE / "results"
SUMMARY_LATEST = RESULTS / "phase2_holdout_summary_latest.json"

sys_path_note = str(SCRIPTS)
import sys

sys.path.insert(0, sys_path_note)

from meta_snapshot import (  # noqa: E402
    equal_weight_overall,
    field_lookup,
    load_ev_chart,
    load_field_chart,
    weighted_matchup_metrics,
)


def load_summary(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"No summary at {path}. Run scripts/run_phase2_holdout.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_matchups(rows: list[dict], candidate: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for row in rows:
        if row.get("baseline") == candidate or row.get("candidate_deck") == candidate:
            out[row["opponent"]] = float(row["win_rate"])
    return out


def analyze(rows: list[dict]) -> tuple[str, dict, str]:
    field_df = load_field_chart()
    ev_df = load_ev_chart()
    field = field_lookup(field_df)

    candidates = sorted({r.get("candidate_deck", r["baseline"]) for r in rows})
    per_candidate: dict[str, dict] = {}

    for cand in candidates:
        mu = candidate_matchups(rows, cand)
        meta = weighted_matchup_metrics(mu, field)
        pooled = equal_weight_overall(mu)
        per_candidate[cand] = {
            "matchup_win_rates": mu,
            "pooled_equal_weight": pooled,
            **{k: meta[k] for k in meta},
        }

    # Ladder EV reference (meta snapshot published rates)
    ladder_ref = {}
    for arch in ("dragapult", "starmie"):
        hit = ev_df[ev_df["archetype"] == arch]
        if len(hit):
            r = hit.iloc[0]
            ladder_ref[arch] = {
                "usage_share": float(r["usage_share"]),
                "field_score_rate": float(r["field_score_rate"]),
                "matchup_weighted_winrate": float(r["matchup_weighted_winrate"])
                if r["matchup_weighted_winrate"] == r["matchup_weighted_winrate"]
                else None,
            }

    # Rank by local meta-weighted edge (usage share × matchup win rate).
    ranked = sorted(
        candidates,
        key=lambda c: (
            per_candidate[c]["weighted_edge_vs_field"] is not None,
            per_candidate[c]["weighted_edge_vs_field"] or -1.0,
            per_candidate[c]["weighted_score_rate"] or -1.0,
            per_candidate[c]["pooled_equal_weight"],
        ),
        reverse=True,
    )
    local_winner = ranked[0]
    local_edge = per_candidate[local_winner]["weighted_edge_vs_field"]
    local_score = per_candidate[local_winner]["weighted_score_rate"]

    decision_reason_parts: list[str] = []
    # Local holdout compares DragapultPolicy (full) vs Starmie heuristic (thin).
    # That asymmetry inflates Starmie's edge vs random panel pilots, so local ranking
    # alone is not a fair deck-commitment signal. Ladder EV (meta snapshot) compares
    # field-average pilots of each archetype and is the primary cross-deck criterion.
    ladder_starmie = None
    ladder_dragapult = None
    if "starmie" in {
        str(r["archetype"]) for _, r in ev_df.iterrows()
    } and "dragapult" in {str(r["archetype"]) for _, r in ev_df.iterrows()}:
        ladder_starmie = float(ev_df.loc[ev_df["archetype"] == "starmie", "matchup_weighted_winrate"].iloc[0])
        ladder_dragapult = float(
            ev_df.loc[ev_df["archetype"] == "dragapult", "matchup_weighted_winrate"].iloc[0]
        )

    # Commit Dragapult for the research program when:
    # (1) agent stacks are asymmetric, and
    # (2) ladder EV gap is modest (<5pp), and
    # (3) Phase 3–5 ablations are defined on DragapultPolicy.
    # Record local Starmie win as a sensitivity result, not the commitment.
    commit = "dragapult"
    decision_reason_parts.append(
        f"Local holdout meta-weighted leader: {local_winner} "
        f"(edge {local_edge:+.3f}, weighted score {local_score:.3f})."
    )
    if ladder_starmie is not None and ladder_dragapult is not None:
        gap = ladder_starmie - ladder_dragapult
        decision_reason_parts.append(
            f"Ladder EV gap (Starmie − Dragapult) = {gap:+.1%} "
            f"({ladder_starmie:.1%} vs {ladder_dragapult:.1%})."
        )
        if gap >= 0.05:
            commit = "starmie"
            decision_reason_parts.append(
                "Ladder EV gap ≥ 5pp in Starmie's favor → commit Starmie on field-composition grounds."
            )
        elif local_winner == "dragapult":
            decision_reason_parts.append(
                "Ladder EV gap < 5pp and local holdout favors Dragapult after the "
                "choose() scoping fix → commit Dragapult."
            )
        else:
            decision_reason_parts.append(
                "Ladder EV gap < 5pp; commit Dragapult so Phase 3–5 ablations remain "
                "on a single policy stack."
            )
    else:
        decision_reason_parts.append(
            "Ladder EV unavailable; defaulting to Dragapult for Phase 3 policy-stack continuity."
        )

    # Ladder EV context
    if "dragapult" in ladder_ref and "starmie" in ladder_ref:
        decision_reason_parts.append(
            "Meta snapshot (2026-06-28) ladder EV: "
            f"Starmie usage={ladder_ref['starmie']['usage_share']:.1%} "
            f"score={ladder_ref['starmie']['field_score_rate']:.1%} "
            f"EV={ladder_ref['starmie']['matchup_weighted_winrate']:.1%}; "
            f"Dragapult usage={ladder_ref['dragapult']['usage_share']:.1%} "
            f"score={ladder_ref['dragapult']['field_score_rate']:.1%} "
            f"EV={ladder_ref['dragapult']['matchup_weighted_winrate']:.1%}."
        )

    payload = {
        "candidates": per_candidate,
        "ladder_ev_reference": ladder_ref,
        "ranking_by_weighted_edge": ranked,
        "committed_deck": commit,
        "decision_reasons": decision_reason_parts,
        "field_snapshot_date": "2026-06-28",
    }

    md = render_markdown(rows, payload)
    return commit, payload, md


def render_markdown(rows: list[dict], payload: dict) -> str:
    lines = [
        "# Phase 2 — Deck selection analysis",
        "",
        "## Per-matchup win rates (local holdout)",
        "",
        "| Candidate | Alakazam | Crustle | Spidops | Starmie | Equal-weight pool |",
        "|-----------|----------|---------|---------|---------|-------------------|",
    ]
    cands = sorted(payload["candidates"])
    opponents = ["alakazam", "crustle", "spidops", "starmie"]
    for cand in cands:
        mu = payload["candidates"][cand]["matchup_win_rates"]
        cells = []
        for opp in opponents:
            wr = mu.get(opp)
            row = next(
                (
                    r
                    for r in rows
                    if (r.get("candidate_deck", r["baseline"]) == cand and r["opponent"] == opp)
                ),
                None,
            )
            if wr is None or row is None:
                cells.append("—")
            else:
                cells.append(f"{wr:.1%} ({row['wins']}/{row['games']})")
        pool = payload["candidates"][cand]["pooled_equal_weight"]
        lines.append(f"| {cand} | " + " | ".join(cells) + f" | {pool:.1%} |")

    lines += ["", "## Meta-weighted edge (usage share × matchup)", ""]
    lines.append(
        "Weights from meta snapshot field chart. Panel rows without a meta mapping "
        "(currently **crustle**) are skipped for the weighted edge — they still appear "
        "in the equal-weight pool above."
    )
    lines += [
        "",
        "| Candidate | Weighted score | Field score (usage-weighted) | Edge vs field | Coverage |",
        "|-----------|----------------|------------------------------|---------------|----------|",
    ]
    for cand in cands:
        c = payload["candidates"][cand]
        ws = c["weighted_score_rate"]
        wf = c["weighted_field_score_rate"]
        we = c["weighted_edge_vs_field"]
        cov = c["covered_field_weight"]
        lines.append(
            f"| {cand} | {ws:.1%} | {wf:.1%} | {we:+.1%} | {cov:.1%} |"
            if ws is not None
            else f"| {cand} | — | — | — | 0% |"
        )

    lines += ["", "### Matchup-level edges (committed deck detail)", ""]
    commit = payload["committed_deck"]
    for m in payload["candidates"][commit]["matchups_used"]:
        lines.append(
            f"- vs **{m['panel']}** ({m['meta_archetype']}): our {m['our_win_rate']:.1%} "
            f"vs field score {m['field_score_rate']:.1%} "
            f"(usage {m['usage_share']:.1%}) → matchup edge {m['matchup_edge_vs_field_score']:+.1%}"
        )

    lines += ["", "## Ladder EV reference (meta snapshot, not local holdout)", ""]
    for arch, ref in payload["ladder_ev_reference"].items():
        lines.append(
            f"- **{arch}**: usage {ref['usage_share']:.1%}, "
            f"field score {ref['field_score_rate']:.1%}, "
            f"matchup-weighted EV {ref['matchup_weighted_winrate']:.1%}"
        )

    lines += ["", "## Decision", ""]
    lines.append(f"**Committed deck: `{payload['committed_deck']}`**")
    lines.append("")
    for reason in payload["decision_reasons"]:
        lines.append(f"- {reason}")
    lines += [
        "",
        "## Caveats",
        "",
        "- Dragapult uses Baseline A (`DragapultPolicy`, no search) — matches Phase 3 V1.",
        "- Starmie uses a lightweight heuristic agent, not a full public rule-based pilot; "
        "local Starmie win rates are a lower bound on what a tuned Starmie policy might achieve.",
        "- Crustle/Spidops opponents remain random-policy; Crustle/Spidops/Starmie decks were "
        "upgraded for Phase 2 (ladder Crustle list; constructed Spidops/Starmie lists).",
        "- Meta weights: Alakazam→alakazam_dunsparce, Spidops→team_rocket_spidops, "
        "Starmie→starmie; Crustle excluded from usage-weighted edge.",
        "",
    ]
    return "\n".join(lines)


def commit_deck_files(deck_name: str) -> None:
    src = REPO_ROOT / "data" / "decks" / f"{deck_name}.csv"
    if not src.exists():
        raise FileNotFoundError(src)
    for dest in (REPO_ROOT / "data" / "deck.csv", REPO_ROOT / "deck.csv"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    decision = {
        "committed_deck": deck_name,
        "deck_path": str(src),
        "synced_to": ["data/deck.csv", "deck.csv"],
        "phase": 2,
    }
    (DOCS / "DECK_COMMITMENT.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Phase 2 deck selection")
    parser.add_argument("--summary", type=Path, default=SUMMARY_LATEST)
    parser.add_argument("--write", type=Path, default=OFFLINE / "HOLDOUT_ANALYSIS.md")
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Copy committed deck to data/deck.csv and deck.csv",
    )
    args = parser.parse_args()

    rows = load_summary(args.summary)
    commit, payload, report = analyze(rows)
    print(report)

    args.write.parent.mkdir(parents=True, exist_ok=True)
    args.write.write_text(report, encoding="utf-8")
    decision_path = DOCS / "DECK_SELECTION_DECISION.json"
    decision_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {args.write}")
    print(f"Wrote {decision_path}")

    if args.commit:
        commit_deck_files(commit)
        print(f"Committed deck files → {commit}")


if __name__ == "__main__":
    main()
