# Phase 1 — Baseline establishment

**Status: COMPLETE** — [`PHASE_01_COMPLETION.md`](PHASE_01_COMPLETION.md)

**Goal:** Working submission + reproducible offline evaluation harness (Baseline A vs B).

| Track | Doc | Analysis | Results (machine-readable) |
|-------|-----|----------|----------------------------|
| **Offline** (local holdout) | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) | [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |
| **Online** (Kaggle ladder) | [KAGGLE_LOG.md](online/KAGGLE_LOG.md) | [KAGGLE_ANALYSIS.md](online/KAGGLE_ANALYSIS.md) | [online/results/](online/results/) |

## Commands

```bash
# Offline — 40 games per opponent (Alakazam, Crustle, Spidops, Starmie)
python scripts/run_phase1_holdout.py --games 40
python scripts/analyze_phase1_results.py

# Online — analyze downloaded ladder replays
python scripts/analyze_kaggle_match_logs.py \
  --rating baseline_a=433 --rating baseline_b=612
```

## Notebooks & code

- Eval notebook: [`notebooks/PHASE_01_BASELINE_EVAL.ipynb`](../../../notebooks/PHASE_01_BASELINE_EVAL.ipynb)
- Holdout runner: [`scripts/holdout_runner.py`](../../../scripts/holdout_runner.py)
- Baselines: [`notebooks/agents/main_baseline_a.py`](../../../notebooks/agents/main_baseline_a.py), [`main_baseline_b.py`](../../../notebooks/agents/main_baseline_b.py)
- Ladder replays: [`logs/phase1_logs/`](../../../logs/phase1_logs/)
