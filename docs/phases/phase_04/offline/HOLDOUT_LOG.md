# Phase 4 holdout log

**Status:** complete

| Item | Value |
|------|-------|
| Agent | V2 (search only, no adaptation) |
| Deck | committed dragapult |
| Panel | v2 |
| Games / matchup | 40 |
| Cells | 7 (two 1-D sweeps; not the full 4×4) |
| Total games | 1,120 (7 × 160) |
| Candidates | [4, 8, 12, 16] |
| Time budgets (s) | [0.5, 1.0, 1.5, 2.0] |
| Seeds | paired `md5(opponent:game_idx)` |
| Policy | `choose_fail=0` on every cell |
| Best cell | `c4_t1500` at 57.5% pooled |
| Submission | **unchanged:** V1 + Dragapult (`main.py`, no search) |

CLI: `python scripts/run_phase4_holdout.py --games 40`
Full grid: add `--grid` (16 cells) — not run.
Analyze: `python scripts/analyze_phase4_results.py`

See [`HOLDOUT_ANALYSIS.md`](HOLDOUT_ANALYSIS.md) for per-matchup rates, curves, and knees.

