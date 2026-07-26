# Phase 1 — Offline holdout log

Local evaluation independent of the Kaggle ladder.

## Completed

- Built **Baseline A** (`notebooks/agents/main_baseline_a.py`) — Dragapult only, no search, no opponent adaptation.
- Built **Baseline B** (`notebooks/agents/main_baseline_b.py`) — Dragapult + UCB1 search, no opponent adaptation.
- Holdout panel under `notebooks/holdout/panel/` — opponents: **Alakazam, Crustle, Spidops, Starmie**.
- Implemented `run_holdout_suite()` in `notebooks/holdout_runner.py`.
- Eval notebook: `notebooks/PHASE_01_BASELINE_EVAL.ipynb`.

## Run

```bash
python notebooks/run_phase1_holdout.py --games 40
python notebooks/analyze_phase1_results.py
```

## Opponent panel notes

| Opponent | Deck | Agent |
|----------|------|-------|
| Alakazam | Meta snapshot payload B | Rule-based agent from meta snapshot |
| Crustle | Placeholder (official sample list) | Random agent |
| Spidops | Placeholder (official sample list) | Random agent |
| Starmie | Placeholder (official sample list) | Random agent |

Replace Crustle / Spidops / Starmie `deck.csv` files when field-accurate lists are available. Baseline A vs B comparisons remain valid as long as both baselines use the same panel.

## Results (40 games/opponent)

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

Search helps vs crustle/spidops/starmie placeholders in the archived run; both baselines struggle vs the rule-based Alakazam agent.

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated holdout EDA |
| [results/phase1_holdout_summary_latest.json](results/phase1_holdout_summary_latest.json) | Latest summary JSON |
| [results/](results/) | Timestamped CSV runs |

Online (Kaggle) results: [../online/KAGGLE_LOG.md](../online/KAGGLE_LOG.md).
