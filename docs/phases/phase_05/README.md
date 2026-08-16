# Phase 5 — Opponent adaptation analysis

**Status: OFFLINE COMPLETE** (traces deferred). See [`PHASE_05_RESULTS.json`](PHASE_05_RESULTS.json) · [`PHASE_05_COMPLETION.md`](PHASE_05_COMPLETION.md)

**Goal:** Show that adaptive weights matter and quantify how much. Paper adaptation section.

| Track | Doc |
|-------|-----|
| Offline V1 vs V3 + detector audit | [offline/HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) |

No new holdout this session: numbers are Phase 3 V1 vs V3 (panel v2, repaired `choose()`).

## Result

Adaptation **hurts**. Pooled V3−V1 = **−5.0 pp**. Intended Crustle cell **−15.0 pp**.

Empty-board early game **cannot false-positive**: detectors only fire on visible active/bench IDs. Panel lists have no unintended ID overlap. No extra archetype detector added.

## Commands

```bash
.venv/bin/python scripts/analyze_phase5_results.py
python docs/research_paper_writeup/generate_phase5_figures.py
```
