# Phase 4 holdout log

**Status:** in progress

| Item | Value |
|------|-------|
| Agent | V2 (UCB1 on, adaptation off) — `notebooks/agents/main_baseline_b.py` |
| Deck | committed Dragapult (`data/decks/dragapult.csv`) |
| Panel | v2 |
| Games / matchup | 40 |
| Default cells | 7 (time sweep at 8 candidates + candidate sweep at 1.5 s) |
| Candidates | 4, 8, 12, 16 |
| Time budgets (s) | 0.5, 1.0, 1.5, 2.0 |
| Seeds | paired `md5(opponent:game_idx)` |
| Policy check | `choose()` must succeed; fail aborts the cell |

CLI: `python scripts/run_phase4_holdout.py --games 40`

Full grid: add `--grid` (16 cells).

Analyze: `python scripts/analyze_phase4_results.py`
