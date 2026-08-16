# Phase 3 — Ablation study

**Status: COMPLETE** — repaired-policy re-run. See [`PHASE_03_COMPLETION.md`](PHASE_03_COMPLETION.md) · [`PHASE_03_RESULTS.json`](PHASE_03_RESULTS.json)

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

## Canonical results (panel v2, repaired `choose()`)

| Version | Alakazam | Crustle | Spidops | Starmie | **Pooled** |
|---------|----------|---------|---------|---------|------------|
| **V1** | 65.0% | 97.5% | 97.5% | 100.0% | **90.0%** (144/160) |
| V2 | 5.0% | 52.5% | 50.0% | 37.5% | 36.2% (58/160) |
| V3 | 60.0% | 82.5% | 100.0% | 97.5% | 85.0% (136/160) |
| V4 | 5.0% | 47.5% | 37.5% | 47.5% | 34.4% (55/160) |

| Contrast | Δ (pp) |
|----------|-------:|
| Search (V2 − V1) | **−53.8** |
| Adaptation (V3 − V1) | **−5.0** |
| Full stack (V4 − V1) | **−55.6** |

`choose_fail=0`. Search executed (V2 `search_ok=1752093`, V4 `search_ok=2104340`).

## Interim research answer

**No** — on panel v2 offline, opponent-adaptive heuristic search does **not** outperform the static Dragapult policy once that policy actually runs. Search is a large regression; adaptation is a small one (Crustle −15.0 pp). Kaggle submission stays **V1 + Dragapult**.

Pre-fix 40.0/32.5/36.2/34.4% table is first-option noise — do not cite.

## Commands

```bash
.venv/bin/python scripts/build_merged_agent.py --variant all
.venv/bin/python scripts/run_phase3_holdout.py --games 40
.venv/bin/python scripts/analyze_phase3_results.py
python docs/research_paper_writeup/generate_phase3_figures.py
```
