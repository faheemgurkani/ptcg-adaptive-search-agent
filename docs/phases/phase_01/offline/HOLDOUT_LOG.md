# Phase 1 — Offline holdout log

Local evaluation independent of the Kaggle ladder.

**Phase 1 status:** complete (A/B/Merged offline) — see [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).

## Completed

- Built **Baseline A** (`notebooks/agents/main_baseline_a.py`) — Dragapult only, no search, no opponent adaptation.
- Built **Baseline B** (`notebooks/agents/main_baseline_b.py`) — Dragapult + UCB1 search, no opponent adaptation.
- Built **Baseline Merged / C** (`notebooks/agents/main_baseline_merged.py` ← `main.py`) — Dragapult + UCB1 + opponent adaptation.
- Holdout panel under `notebooks/holdout/panel/` — opponents: **Alakazam, Crustle, Spidops, Starmie**.
- Implemented `run_holdout_suite()` in `scripts/holdout_runner.py` (real `cabt` simulations via `kaggle_environments`).
- Eval notebook: `notebooks/PHASE_01_BASELINE_EVAL.ipynb`.

## Run

```bash
# A + B
python scripts/run_phase1_holdout.py --games 40 --baselines baseline_a baseline_b

# Merged only (merge into latest JSON)
python scripts/run_phase1_holdout.py --games 40 --baselines baseline_merged --merge-latest

python scripts/analyze_phase1_results.py
```

## Opponent panel notes

| Opponent | Deck | Agent |
|----------|------|-------|
| Alakazam | Meta snapshot payload B | Rule-based agent from meta snapshot |
| Crustle | Placeholder (official sample list) | Random agent |
| Spidops | Placeholder (official sample list) | Random agent |
| Starmie | Placeholder (official sample list) | Random agent |

Replace Crustle / Spidops / Starmie `deck.csv` files when field-accurate lists are available. Comparisons remain valid as long as all baselines use the same panel.

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
| baseline_merged | alakazam | 0.025 | 1/40 | fail |
| baseline_merged | crustle | 0.300 | 12/40 | fail |
| baseline_merged | spidops | 0.750 | 30/40 | pass |
| baseline_merged | starmie | 0.600 | 24/40 | pass |

**Pooled (160 games each):**

| Baseline | Flags | Pooled WR | Record |
|----------|-------|----------:|--------|
| A | no search, no adaptation | **66.2%** | 106/160 |
| B | search, no adaptation | **63.7%** | 102/160 |
| Merged (C) | search + adaptation | **41.9%** | 67/160 |

| Contrast | Δ |
|----------|--:|
| Search (B − A) | **−2.5 pp** |
| Adaptation on search (Merged − B) | **−21.9 pp** |
| Full stack (Merged − A) | **−24.4 pp** |

**Interpretation:** On this fixed panel, enabling opponent-adaptation hooks **hurt** offline win rate sharply (especially vs placeholder Crustle: 30% vs B’s 85%). Note Crustle/Spidops/Starmie remain placeholder decks + random agents — the Crustle detector may fire incorrectly or adaptation weights may be miscalibrated. Alakazam (real rule-based) also worsens (2.5% vs B 15%). Treat Merged’s offline result as a **negative adaptation finding** pending ladder logs and better panel decks.

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated holdout EDA (A/B/Merged) |
| [results/phase1_holdout_summary_latest.json](results/phase1_holdout_summary_latest.json) | Latest summary JSON |
| [results/](results/) | Timestamped CSV runs (incl. `*_20260729T132234Z*` for merged) |

Online (Kaggle) results: [../online/KAGGLE_LOG.md](../online/KAGGLE_LOG.md).
