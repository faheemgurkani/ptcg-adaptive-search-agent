# Phase 1 — Baseline establishment

**Status:** A/B/Merged offline complete (all **first-option stubs**); A/B online complete (same stub, sample-water); Merged ladder not ingested — [`PHASE_01_COMPLETION.md`](PHASE_01_COMPLETION.md)

**Goal:** Working submission + reproducible offline evaluation harness (A / B / Merged).

| Track | Doc | Analysis | Results (machine-readable) |
|-------|-----|----------|----------------------------|
| **Offline** (local holdout) | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) | [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |
| **Online** (Kaggle ladder) | [KAGGLE_LOG.md](online/KAGGLE_LOG.md) | [KAGGLE_ANALYSIS.md](online/KAGGLE_ANALYSIS.md) | [online/results/](online/results/) |

## Commands

```bash
# Offline — 40 games per opponent × baselines
python scripts/run_phase1_holdout.py --games 40 --baselines baseline_a baseline_b
python scripts/run_phase1_holdout.py --games 40 --baselines baseline_merged --merge-latest
python scripts/analyze_phase1_results.py

# Online — analyze downloaded ladder replays
python scripts/analyze_kaggle_match_logs.py \
  --rating baseline_a=507 --rating baseline_b=507
```

## Notebooks & code

- Eval notebook: [`notebooks/PHASE_01_BASELINE_EVAL.ipynb`](../../../notebooks/PHASE_01_BASELINE_EVAL.ipynb)
- Holdout runner: [`scripts/holdout_runner.py`](../../../scripts/holdout_runner.py)
- Baselines: [`main_baseline_a.py`](../../../notebooks/agents/main_baseline_a.py), [`main_baseline_b.py`](../../../notebooks/agents/main_baseline_b.py), [`main_baseline_merged.py`](../../../notebooks/agents/main_baseline_merged.py)
- Ladder replays: [`logs/phase1_logs/`](../../../logs/phase1_logs/)
