# Phase 1 — Baseline Establishment (local log)

## Completed locally

- Built **Baseline A** (`notebooks/agents/main_baseline_a.py`) — Dragapult only, no search, no opponent adaptation.
- Built **Baseline B** (`notebooks/agents/main_baseline_b.py`) — Dragapult + UCB1 search, no opponent adaptation.
- Holdout panel under `notebooks/holdout/panel/` — opponents: **Alakazam, Crustle, Spidops, Starmie** (Phase 1 research doc panel).
- Implemented `run_holdout_suite()` in `notebooks/holdout_runner.py`.
- Eval notebook: `notebooks/PHASE_01_BASELINE_EVAL.ipynb`.
- Run script: `python notebooks/run_phase1_holdout.py --games 40`.

## Opponent panel notes

| Opponent | Deck | Agent |
|----------|------|-------|
| Alakazam | Meta snapshot payload B | Rule-based agent from meta snapshot |
| Crustle | Placeholder (official sample list) | Random agent |
| Spidops | Placeholder (official sample list) | Random agent |
| Starmie | Placeholder (official sample list) | Random agent |

Replace Crustle / Spidops / Starmie `deck.csv` files when field-accurate lists are available. Baseline A vs B comparisons remain valid as long as both baselines use the same panel.

## Results (local holdout, 40 games/opponent)

| Baseline | Opponent | Win rate | Record |
|----------|----------|----------|--------|
| baseline_a | alakazam | 0.100 | 4/40 |
| baseline_a | crustle | 0.725 | 29/40 |
| baseline_a | spidops | 0.750 | 30/40 |
| baseline_a | starmie | 0.775 | 31/40 |
| baseline_b | alakazam | 0.125 | 5/40 |
| baseline_b | crustle | 0.800 | 32/40 |
| baseline_b | spidops | 0.850 | 34/40 |
| baseline_b | starmie | 0.750 | 30/40 |

Search helps vs crustle/spidops/starmie placeholders in this run; both baselines struggle vs the rule-based Alakazam agent.

Latest machine-readable summary: `notebooks/output/phase1/phase1_holdout_summary_latest.json`

## Results (archive)

## Your Kaggle tasks (Phase 1)

1. Package **Baseline A** from `notebooks/agents/main_baseline_a.py` + active `deck.csv` + `cg/` → submit once → record ladder rating.
2. Package **Baseline B** from `notebooks/agents/main_baseline_b.py` + active `deck.csv` + `cg/` → submit once → record ladder rating.
3. Log ratings here or in your experiment notes for comparison with local holdout direction.

Use workbench section 6 (`build_submission()`) but point `PATHS.main_py` at the chosen baseline file before packaging.
