# Phase 1 — Offline holdout log

Local evaluation independent of the Kaggle ladder.

**Phase 1 status:** complete — see [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).

## Completed

- Built **Baseline A** (`notebooks/agents/main_baseline_a.py`) — Dragapult only, no search, no opponent adaptation.
- Built **Baseline B** (`notebooks/agents/main_baseline_b.py`) — Dragapult + UCB1 search, no opponent adaptation.
- Holdout panel under `notebooks/holdout/panel/` — opponents: **Alakazam, Crustle, Spidops, Starmie**.
- Implemented `run_holdout_suite()` in `scripts/holdout_runner.py` (real `cabt` simulations via `kaggle_environments`).
- Eval notebook: `notebooks/PHASE_01_BASELINE_EVAL.ipynb`.

## Run

```bash
python scripts/run_phase1_holdout.py --games 40
python scripts/analyze_phase1_results.py
```

## Opponent panel notes

| Opponent | Deck | Agent |
|----------|------|-------|
| Alakazam | Meta snapshot payload B | Rule-based agent from meta snapshot |
| Crustle | Placeholder (official sample list) | Random agent |
| Spidops | Placeholder (official sample list) | Random agent |
| Starmie | Placeholder (official sample list) | Random agent |

Replace Crustle / Spidops / Starmie `deck.csv` files when field-accurate lists are available. Baseline A vs B comparisons remain valid as long as both baselines use the same panel.

## Results (canonical — 40 games/opponent)

Source: [`results/phase1_holdout_summary_latest.json`](results/phase1_holdout_summary_latest.json)

| Baseline | Opponent | Win rate | Record | Gate (≥52%) |
|----------|----------|---------:|--------|-------------|
| baseline_a | alakazam | 0.200 | 8/40 | fail |
| baseline_a | crustle | 0.775 | 31/40 | pass |
| baseline_a | spidops | 0.850 | 34/40 | pass |
| baseline_a | starmie | 0.825 | 33/40 | pass |
| baseline_b | alakazam | 0.150 | 6/40 | fail |
| baseline_b | crustle | 0.850 | 34/40 | pass |
| baseline_b | spidops | 0.750 | 30/40 | pass |
| baseline_b | starmie | 0.800 | 32/40 | pass |

**Pooled:** Baseline A 66.2% (106/160), Baseline B 63.7% (102/160), search Δ −2.5 pp.

Both baselines fail the holdout gate vs the rule-based Alakazam agent. Search is mixed offline (helps Crustle, hurts Spidops/Starmie/Alakazam in this run) while still providing clean A/B ablation labels for the paper.

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated holdout EDA |
| [results/phase1_holdout_summary_latest.json](results/phase1_holdout_summary_latest.json) | Latest summary JSON |
| [results/](results/) | Timestamped CSV runs |

Online (Kaggle) results: [../online/KAGGLE_LOG.md](../online/KAGGLE_LOG.md).
