# Phase 4 holdout log

**Status:** complete

| Item | Value |
|------|-------|
| Agent | V2 (search only, no adaptation) |
| Deck | dragapult |
| Panel | v2 |
| Games / matchup | 40 |
| Cells | 7 |
| Candidates | [4, 8, 12, 16] |
| Time budgets (s) | [0.5, 1.0, 1.5, 2.0] |
| Seeds | paired `md5(opponent:game_idx)` |

CLI: `python scripts/run_phase4_holdout.py --games 40`
Full grid: add `--grid` (16 cells).
Analyze: `python scripts/analyze_phase4_results.py`

