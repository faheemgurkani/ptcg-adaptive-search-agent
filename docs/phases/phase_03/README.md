# Phase 3 — Ablation study

**Status:** in progress — see [`PHASE_03_COMPLETION.md`](PHASE_03_COMPLETION.md)

**Goal:** Isolate search vs adaptation on committed Dragapult deck (panel v2).

| Track | Doc | Results |
|-------|-----|---------|
| **Offline** ablation V1–V4 | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) · [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |

## Ablation matrix

| Version | Search | Adaptation | Agent file |
|---------|:------:|:----------:|------------|
| V1 | ✗ | ✗ | `notebooks/agents/main_baseline_a.py` |
| V2 | ✓ UCB1 | ✗ | `notebooks/agents/main_baseline_b.py` |
| V3 | ✗ | ✓ | `notebooks/agents/main_baseline_v3.py` |
| V4 | ✓ UCB1 | ✓ | `notebooks/agents/main_baseline_merged.py` |

Deck: committed **Dragapult** (`data/decks/dragapult.csv`). Panel: **v2**.

## Commands

```bash
.venv/bin/python scripts/build_merged_agent.py --variant baseline_v3   # if V3 missing
.venv/bin/python scripts/run_phase3_holdout.py --games 40
.venv/bin/python scripts/analyze_phase3_results.py
```
