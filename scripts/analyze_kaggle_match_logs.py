#!/usr/bin/env python3
"""EDA for Kaggle ladder match replay JSON logs (phase / baseline wise)."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
DOCS = REPO_ROOT / "docs"
DEFAULT_LOG_ROOT = REPO_ROOT / "logs" / "phase1_logs"
DEFAULT_PANEL = REPO_ROOT / "notebooks" / "holdout" / "panel"
DEFAULT_OUT = DOCS / "phases" / "phase_01" / "online"

OUR_AGENT_NAME = "Muhammad Faheem"
OUR_DECK_SIGNATURE = {119, 120, 121}  # Dreepy / Drakloak / Dragapult-ex
SAMPLE_WATER_SIGNATURE = {3, 721, 722, 723, 1145, 1158, 1205, 1227, 1235}


@dataclass
class MatchRecord:
    phase: str
    baseline: str
    folder_label: str
    episode_id: int | None
    path: str
    our_player: int
    won: bool
    folder_matches_outcome: bool
    rewards: list[int]
    steps: int
    our_decisions: int
    opp_decisions: int
    opp_deck_unique_count: int
    opp_deck_unique: list[int]
    opp_archetype: str
    opp_archetype_score: float
    opp_cards_seen: int
    top_opp_board_cards: list[tuple[int, int]]
    our_hand_range: tuple[int | None, int | None] | None
    opp_hand_range: tuple[int | None, int | None] | None


def load_deck_signatures(panel_dir: Path) -> dict[str, set[int]]:
    sigs: dict[str, set[int]] = {}
    if not panel_dir.is_dir():
        return sigs
    for sub in sorted(panel_dir.iterdir()):
        deck = sub / "deck.csv"
        if deck.is_file():
            ids = {
                int(line.strip())
                for line in deck.read_text(encoding="utf-8").splitlines()
                if line.strip().isdigit()
            }
            if ids:
                sigs[sub.name] = ids
    return sigs


def classify_opponent_deck(unique_ids: list[int] | None, signatures: dict[str, set[int]]) -> tuple[str, float]:
    if not unique_ids:
        return "unknown", 0.0
    deck = set(unique_ids)
    best_name = "unclassified"
    best_score = 0.0
    for name, sig in signatures.items():
        overlap = len(deck & sig)
        denom = max(len(sig), 1)
        score = overlap / denom
        if score > best_score:
            best_score = score
            best_name = name
    if best_score >= 0.45:
        return best_name, best_score
    if len(deck & OUR_DECK_SIGNATURE) >= 3:
        return "mirror_dragapult", best_score
    if len(deck & SAMPLE_WATER_SIGNATURE) >= 5:
        return "sample_wugtrio_water", best_score
    return f"other_{len(deck)}_types", best_score


def infer_our_player(data: dict) -> int:
    info = data.get("info") or {}
    agents = info.get("Agents") or []
    for i, agent in enumerate(agents):
        name = agent.get("Name") if isinstance(agent, dict) else ""
        if name == OUR_AGENT_NAME:
            return i
    steps = data.get("steps") or []
    for pi in (0, 1):
        try:
            action = steps[1][pi].get("action")
            if isinstance(action, list) and len(action) == 60:
                ids = set(int(x) for x in action)
                if OUR_DECK_SIGNATURE <= ids or len(ids & OUR_DECK_SIGNATURE) >= 3:
                    return pi
        except (IndexError, TypeError, AttributeError, ValueError):
            continue
    rewards = data.get("rewards") or [0, 0]
    return 0 if rewards[0] >= rewards[1] else 1


def extract_match(
    path: Path,
    log_root: Path,
    phase: str,
    baseline: str,
    folder_label: str,
    signatures: dict[str, set[int]],
) -> MatchRecord:
    data = json.loads(path.read_text(encoding="utf-8"))
    our_player = infer_our_player(data)
    rewards = data.get("rewards") or [0, 0]
    won = rewards[our_player] == 1
    steps = data.get("steps") or []
    opp_player = 1 - our_player

    our_decisions = 0
    opp_decisions = 0
    opp_deck_unique: list[int] | None = None
    opp_visible: Counter[int] = Counter()
    our_hand: list[int | None] = []
    opp_hand: list[int | None] = []

    for step in steps:
        if not isinstance(step, list) or len(step) < 2:
            continue
        for slot, bucket in ((our_player, "our"), (opp_player, "opp")):
            action = step[slot].get("action")
            if isinstance(action, list) and len(action) not in (0, 60):
                if bucket == "our":
                    our_decisions += 1
                else:
                    opp_decisions += 1
        if opp_deck_unique is None:
            opp_action = step[opp_player].get("action")
            if isinstance(opp_action, list) and len(opp_action) == 60:
                opp_deck_unique = sorted(set(opp_action))

        obs = (step[our_player].get("observation") or {}).get("current") or {}
        your_index = obs.get("yourIndex")
        players = obs.get("players") or []
        if your_index is None or len(players) < 2:
            continue
        you = players[your_index]
        opp = players[1 - your_index]
        our_hand.append(you.get("handCount"))
        opp_hand.append(opp.get("handCount"))
        for zone in ("active", "bench", "discard"):
            for card in (opp.get(zone) or []):
                if isinstance(card, dict) and card.get("id") is not None:
                    opp_visible[int(card["id"])] += 1

    def hand_range(values: list[int | None]) -> tuple[int | None, int | None] | None:
        nums = [v for v in values if v is not None]
        return (min(nums), max(nums)) if nums else None

    archetype, score = classify_opponent_deck(opp_deck_unique, signatures)

    return MatchRecord(
        phase=phase,
        baseline=baseline,
        folder_label=folder_label,
        episode_id=(data.get("info") or {}).get("EpisodeId"),
        path=str(path.relative_to(log_root)),
        our_player=our_player,
        won=won,
        folder_matches_outcome=(folder_label == "won") == won,
        rewards=rewards,
        steps=len(steps),
        our_decisions=our_decisions,
        opp_decisions=opp_decisions,
        opp_deck_unique_count=len(opp_deck_unique or []),
        opp_deck_unique=opp_deck_unique or [],
        opp_archetype=archetype,
        opp_archetype_score=round(score, 3),
        opp_cards_seen=len(opp_visible),
        top_opp_board_cards=[(k, v) for k, v in opp_visible.most_common(8)],
        our_hand_range=hand_range(our_hand),
        opp_hand_range=hand_range(opp_hand),
    )


def discover_matches(log_root: Path, signatures: dict[str, set[int]]) -> list[MatchRecord]:
    records: list[MatchRecord] = []
    for path in sorted(log_root.rglob("*.json")):
        rel = path.relative_to(log_root)
        parts = rel.parts
        if len(parts) >= 3 and parts[1] in {"won", "lost"}:
            phase = parts[0] if parts[0].startswith("phase") or parts[0].startswith("baseline") else "phase1"
            baseline = parts[0]
            folder = parts[1]
        elif len(parts) == 1:
            phase = "phase1"
            baseline = "unsorted"
            folder = "unknown"
        else:
            continue
        records.append(extract_match(path, log_root, phase, baseline, folder, signatures))
    return records


def summarize_baseline(rows: list[MatchRecord]) -> dict:
    wins = sum(1 for r in rows if r.won)
    games = len(rows)
    win_steps = [r.steps for r in rows if r.won]
    loss_steps = [r.steps for r in rows if not r.won]
    return {
        "games": games,
        "wins": wins,
        "losses": games - wins,
        "win_rate": round(wins / games, 4) if games else 0.0,
        "avg_steps_wins": round(statistics.mean(win_steps), 1) if win_steps else None,
        "avg_steps_losses": round(statistics.mean(loss_steps), 1) if loss_steps else None,
        "player_slot_p0": sum(1 for r in rows if r.our_player == 0),
        "player_slot_p1": sum(1 for r in rows if r.our_player == 1),
        "label_mismatches": sum(1 for r in rows if not r.folder_matches_outcome),
    }


def archetype_table(rows: list[MatchRecord]) -> list[dict]:
    grouped: dict[str, list[MatchRecord]] = defaultdict(list)
    for row in rows:
        grouped[row.opp_archetype].append(row)
    out = []
    for name, items in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        wins = sum(1 for r in items if r.won)
        out.append(
            {
                "opponent_archetype": name,
                "games": len(items),
                "wins": wins,
                "win_rate": round(wins / len(items), 4),
            }
        )
    return out


def render_markdown(
    records: list[MatchRecord],
    ladder_ratings: dict[str, int | None],
    log_root: Path,
) -> str:
    by_baseline: dict[str, list[MatchRecord]] = defaultdict(list)
    for row in records:
        by_baseline[row.baseline].append(row)

    lines = [
        "# Phase 1 — Kaggle ladder log analysis",
        "",
        f"Log root: `{log_root}`",
        "",
        "## Ladder ratings (from Kaggle UI — not in JSON logs)",
        "",
    ]
    for baseline in sorted(by_baseline):
        rating = ladder_ratings.get(baseline)
        lines.append(f"- **{baseline}:** {rating if rating is not None else 'not provided'}")
    lines.append("")
    lines.append(
        "> Replay JSON files cover only downloaded episodes. Win rates below are **sample** stats, "
        "not the full ladder record that produced the rating."
    )
    lines.append("")

    lines.append("## Baseline summary (logged episodes)")
    lines.append("")
    lines.append("| Baseline | Games | Wins | Losses | Win rate | Avg steps (W/L) | P0/P1 slots |")
    lines.append("|----------|------:|-----:|-------:|---------:|-----------------|-------------|")
    for baseline in sorted(by_baseline):
        s = summarize_baseline(by_baseline[baseline])
        avg = (
            f"{s['avg_steps_wins']}/{s['avg_steps_losses']}"
            if s["avg_steps_wins"] is not None
            else "—"
        )
        lines.append(
            f"| {baseline} | {s['games']} | {s['wins']} | {s['losses']} | "
            f"{s['win_rate']:.1%} | {avg} | {s['player_slot_p0']}/{s['player_slot_p1']} |"
        )
    lines.append("")

    if len(by_baseline) >= 2:
        a = summarize_baseline(by_baseline["baseline_a"])
        b = summarize_baseline(by_baseline["baseline_b"])
        lines.append("## Baseline A vs B")
        lines.append("")
        lines.append(
            f"- Logged sample win rate: B {b['win_rate']:.1%} ({b['wins']}/{b['games']}) "
            f"vs A {a['win_rate']:.1%} ({a['wins']}/{a['games']}) → **B +{(b['win_rate']-a['win_rate'])*100:.1f} pp**"
        )
        ra, rb = ladder_ratings.get("baseline_a"), ladder_ratings.get("baseline_b")
        if ra is not None and rb is not None:
            lines.append(f"- Ladder rating: B **{rb}** vs A **{ra}** → **+{rb - ra}** (aligns with search helping on ladder)")
        lines.append("")

    for baseline in sorted(by_baseline):
        rows = by_baseline[baseline]
        lines.append(f"## {baseline} — opponent archetypes (deck-submit heuristic)")
        lines.append("")
        lines.append("| Opponent archetype | Games | Wins | Win rate |")
        lines.append("|--------------------|------:|-----:|---------:|")
        for row in archetype_table(rows):
            lines.append(
                f"| {row['opponent_archetype']} | {row['games']} | {row['wins']} | {row['win_rate']:.1%} |"
            )
        lines.append("")

        lines.append(f"## {baseline} — per-episode detail")
        lines.append("")
        lines.append(
            "| Episode | Folder | Result | Steps | Slot | Opp archetype | Opp unique types | Top opp board cards |"
        )
        lines.append("|---------|--------|--------|------:|------|---------------|-----------------:|---------------------|")
        for r in sorted(rows, key=lambda x: x.episode_id or 0):
            top = ", ".join(f"{cid}×{n}" for cid, n in r.top_opp_board_cards[:4]) or "—"
            lines.append(
                f"| {r.episode_id} | {r.folder_label} | {'W' if r.won else 'L'} | {r.steps} | "
                f"P{r.our_player} | {r.opp_archetype} | {r.opp_deck_unique_count} | {top} |"
            )
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- **Player slot** alternates on the ladder; infer wins from `rewards[our_player]`, not raw `rewards[0]`.")
    lines.append("- **Opponent identity** (username / submission id) is not present in logs — only deck lists and board-visible cards.")
    lines.append("- **Archetype labels** compare opponent deck-submit unique IDs to holdout panel signatures; `other_N_types` = field deck not in panel.")
    lines.append("- Re-run: `python scripts/analyze_kaggle_match_logs.py --rating baseline_a=433 --rating baseline_b=612`")
    lines.append("- Docs: `docs/phases/phase_01/online/KAGGLE_LOG.md`")
    lines.append("")
    return "\n".join(lines)


def parse_ratings(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in values:
        if "=" not in item:
            continue
        key, val = item.split("=", 1)
        out[key.strip()] = int(val.strip())
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Kaggle ladder match replay logs")
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--rating",
        action="append",
        default=[],
        help="Ladder rating from UI, e.g. baseline_a=433",
    )
    parser.add_argument("--phase", default="phase1", help="Phase label written into JSON output")
    args = parser.parse_args()

    signatures = load_deck_signatures(args.panel)
    records = discover_matches(args.log_root, signatures)
    if not records:
        print(f"No JSON logs found under {args.log_root}", file=sys.stderr)
        sys.exit(1)

    ratings = parse_ratings(args.rating)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "phase": args.phase,
        "log_root": str(args.log_root),
        "ladder_ratings": ratings,
        "matches": [asdict(r) for r in records],
        "baseline_summary": {
            b: summarize_baseline([r for r in records if r.baseline == b])
            for b in sorted({r.baseline for r in records})
        },
        "baseline_archetypes": {
            b: archetype_table([r for r in records if r.baseline == b])
            for b in sorted({r.baseline for r in records})
        },
    }

    json_path = args.out_dir / "results" / "kaggle_log_analysis.json"
    md_path = args.out_dir / "KAGGLE_ANALYSIS.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(records, ratings, args.log_root), encoding="utf-8")

    print(render_markdown(records, ratings, args.log_root))
    print(f"\nWrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
