# Phase 4 — Search depth analysis

**Status: COMPLETE** — see [`PHASE_04_RESULTS.json`](PHASE_04_RESULTS.json)

**Goal:** How much UCB1 search depth matters under a wall-clock budget. Paper **Figure 2**.

| Track | Doc | Results |
|-------|-----|---------|
| **Offline** V2 sweep | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) · [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |

## Protocol

- Agent: **V2** (search on, adaptation off) + committed Dragapult + panel v2.
- Candidates: 4, 8, 12, 16. Time: 0.5, 1.0, 1.5, 2.0 s.
- Default run: two 1-D sweeps (8 candidates × all times; 1.5 s × all candidate counts) = 7 cells × 160 games.
- `--grid` runs the full 4×4 (16 cells).

## Result

Best cell `c4_t1500` at **57.5%** pooled (−32.5 pp vs V1). Time knee 0.5 s; candidate knee 4. Extra search compute does not recover the static policy.

## Commands

```bash
.venv/bin/python scripts/build_merged_agent.py --variant baseline_b
.venv/bin/python scripts/run_phase4_holdout.py --games 40
.venv/bin/python scripts/analyze_phase4_results.py
python docs/research_paper_writeup/generate_phase4_figures.py
```

