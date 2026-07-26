# Phase 1 — Kaggle ladder log analysis

Log root: `/Volumes/Sandisk 2TB/Documents/Hackathons and Competitions/Kaggle - PTCG/logs/phase1_logs`

## Ladder ratings (from Kaggle UI — not in JSON logs)

- **baseline_a:** 433
- **baseline_b:** 612

> Replay JSON files cover only downloaded episodes. Win rates below are **sample** stats, not the full ladder record that produced the rating.

## Baseline summary (logged episodes)

| Baseline | Games | Wins | Losses | Win rate | Avg steps (W/L) | P0/P1 slots |
|----------|------:|-----:|-------:|---------:|-----------------|-------------|
| baseline_a | 9 | 4 | 5 | 44.4% | 75.2/68.6 | 6/3 |
| baseline_b | 10 | 5 | 5 | 50.0% | 71.4/71.8 | 8/2 |

## Baseline A vs B

- Logged sample win rate: B 50.0% (5/10) vs A 44.4% (4/9) → **B +5.6 pp**
- Ladder rating: B **612** vs A **433** → **+179** (aligns with search helping on ladder)

## baseline_a — opponent archetypes (deck-submit heuristic)

| Opponent archetype | Games | Wins | Win rate |
|--------------------|------:|-----:|---------:|
| other_19_types | 4 | 1 | 25.0% |
| other_18_types | 2 | 2 | 100.0% |
| crustle | 1 | 0 | 0.0% |
| other_16_types | 1 | 0 | 0.0% |
| other_20_types | 1 | 1 | 100.0% |

## baseline_a — per-episode detail

| Episode | Folder | Result | Steps | Slot | Opp archetype | Opp unique types | Top opp board cards |
|---------|--------|--------|------:|------|---------------|-----------------:|---------------------|
| 88299992 | lost | L | 92 | P0 | other_19_types | 19 | 37×211, 345×182, 1227×172, 1182×146 |
| 88300519 | won | W | 20 | P1 | other_19_types | 19 | 112×15, 7×2 |
| 88301029 | lost | L | 48 | P0 | crustle | 9 | 3×60, 1205×46, 723×44, 721×43 |
| 88301557 | lost | L | 55 | P0 | other_16_types | 16 | 169×81, 666×76, 1227×54, 1122×54 |
| 88302078 | won | W | 98 | P0 | other_18_types | 18 | 7×520, 112×194, 646×182, 1086×112 |
| 88302605 | lost | L | 111 | P1 | other_19_types | 19 | 2×300, 352×238, 1215×195, 1152×135 |
| 88303144 | won | W | 70 | P1 | other_18_types | 18 | 6×200, 673×119, 1227×104, 1192×69 |
| 88303662 | lost | L | 37 | P0 | other_19_types | 19 | 878×51, 65×50, 304×31, 1227×28 |
| 88304270 | won | W | 113 | P0 | other_20_types | 20 | 7×296, 1219×173, 646×157, 112×142 |

## baseline_b — opponent archetypes (deck-submit heuristic)

| Opponent archetype | Games | Wins | Win rate |
|--------------------|------:|-----:|---------:|
| alakazam | 2 | 1 | 50.0% |
| other_17_types | 2 | 1 | 50.0% |
| other_18_types | 1 | 0 | 0.0% |
| other_19_types | 1 | 1 | 100.0% |
| other_20_types | 1 | 0 | 0.0% |
| other_22_types | 1 | 0 | 0.0% |
| other_24_types | 1 | 1 | 100.0% |
| other_9_types | 1 | 1 | 100.0% |

## baseline_b — per-episode detail

| Episode | Folder | Result | Steps | Slot | Opp archetype | Opp unique types | Top opp board cards |
|---------|--------|--------|------:|------|---------------|-----------------:|---------------------|
| 88299983 | lost | L | 58 | P1 | alakazam | 20 | 741×96, 305×68, 742×66, 1152×46 |
| 88300502 | lost | L | 85 | P0 | other_20_types | 20 | 311×174, 878×154, 879×97, 1219×85 |
| 88301030 | won | W | 80 | P0 | other_24_types | 24 | 1×175, 655×124, 96×117, 1100×63 |
| 88301549 | lost | L | 73 | P0 | other_18_types | 18 | 344×123, 345×116, 1086×114, 1227×78 |
| 88302072 | won | W | 62 | P0 | other_19_types | 19 | 333×129, 1227×114, 6×67, 678×63 |
| 88302593 | lost | L | 82 | P1 | other_22_types | 22 | 235×150, 1120×115, 1086×104, 120×76 |
| 88303131 | won | W | 20 | P0 | other_9_types | 9 | 96×15, 1×4 |
| 88303651 | won | W | 75 | P0 | other_17_types | 17 | 112×183, 7×107, 305×87, 1231×56 |
| 88304240 | lost | L | 61 | P0 | other_17_types | 17 | 1152×99, 677×66, 673×66, 676×55 |
| 88304775 | won | W | 120 | P0 | alakazam | 23 | 741×302, 1152×266, 1079×162, 1086×139 |

## Notes

- **Player slot** alternates on the ladder; infer wins from `rewards[our_player]`, not raw `rewards[0]`.
- **Opponent identity** (username / submission id) is not present in logs — only deck lists and board-visible cards.
- **Archetype labels** compare opponent deck-submit unique IDs to holdout panel signatures; `other_N_types` = field deck not in panel.
- Re-run: `python notebooks/analyze_kaggle_match_logs.py --rating baseline_a=433 --rating baseline_b=612`
- Docs: `docs/phases/phase_01/online/KAGGLE_LOG.md`
