# Phase 3 — Ablation study

**Status: COMPLETE** — see [`PHASE_03_COMPLETION.md`](PHASE_03_COMPLETION.md) · [`PHASE_03_RESULTS.json`](PHASE_03_RESULTS.json)

**Goal:** Isolate search vs adaptation on committed Dragapult deck (panel v2). Paper **Table 1**.

| Track | Doc | Results |
|-------|-----|---------|
| **Offline** ablation V1–V4 | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) · [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) · [PHASE_03_RESULTS.json](PHASE_03_RESULTS.json) |

## Ablation matrix

| Version | Search | Adaptation | Agent file |
|---------|:------:|:----------:|------------|
| V1 | ✗ | ✗ | `notebooks/agents/main_baseline_a.py` |
| V2 | ✓ UCB1 | ✗ | `notebooks/agents/main_baseline_b.py` |
| V3 | ✗ | ✓ | `notebooks/agents/main_baseline_v3.py` |
| V4 | ✓ UCB1 | ✓ | `notebooks/agents/main_baseline_merged.py` |

Deck: committed **Dragapult** (`data/decks/dragapult.csv`). Panel: **v2**. **640 games** (40 × 4 × 4).

## Canonical results (panel v2)

| Version | Alakazam | Crustle | Spidops | Starmie | **Pooled** |
|---------|----------|---------|---------|---------|------------|
| **V1** | 7.5% | 27.5% | 72.5% | 52.5% | **40.0%** (64/160) |
| V2 | 5.0% | 27.5% | 65.0% | 32.5% | 32.5% (52/160) |
| V3 | 5.0% | 20.0% | 70.0% | 50.0% | 36.2% (58/160) |
| V4 | 2.5% | 27.5% | 67.5% | 40.0% | 34.4% (55/160) |

| Contrast | Δ (pp) |
|----------|-------:|
| Search (V2 − V1) | **−7.5** |
| Adaptation (V3 − V1) | **−3.8** |
| Full stack (V4 − V1) | **−5.6** |

## Interim research answer

**No** — on panel v2 offline, opponent-adaptive heuristic search does **not** outperform the static Dragapult policy. V1 wins; search hurts most vs Starmie (−20 pp); adaptation hurts vs Crustle (−7.5 pp, hypothesis fails). Kaggle submission stays **V1 + Dragapult** (Phase 2 commitment).

## Commands

```bash
.venv/bin/python scripts/build_merged_agent.py --variant baseline_v3   # if V3 missing
.venv/bin/python scripts/run_phase3_holdout.py --games 40
.venv/bin/python scripts/analyze_phase3_results.py
python docs/research_paper_writeup/generate_phase3_figures.py
```
