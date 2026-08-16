# Phase 2 — Deck selection & meta analysis

**Status: COMPLETE** — committed deck: **Dragapult** (canonical re-run after `choose()` fix)

**Goal:** Pick and commit to one deck with a principled justification before Phase 3 ablations.

| Track | Doc | Results |
|-------|-----|---------|
| **Offline** holdout + meta edge | [HOLDOUT_LOG.md](offline/HOLDOUT_LOG.md) · [HOLDOUT_ANALYSIS.md](offline/HOLDOUT_ANALYSIS.md) | [offline/results/](offline/results/) |
| **Decision** | [DECK_SELECTION_DECISION.json](DECK_SELECTION_DECISION.json) · [DECK_COMMITMENT.json](DECK_COMMITMENT.json) | `data/decks/dragapult.csv` → `data/deck.csv` |

## Commands

```bash
# from repo root, use project venv
.venv/bin/python scripts/run_phase2_holdout.py --games 40
.venv/bin/python scripts/analyze_phase2_results.py --commit
```

## Commitment (freeze before Phase 3)

| Field | Value |
|-------|-------|
| Deck | **Dragapult** |
| List | `data/decks/dragapult.csv` (synced to `data/deck.csv`) |
| Agent stack | `DragapultPolicy` (Baseline A / V1) |
| Canonical holdout | Dragapult **83.1%** vs Starmie **58.8%** (panel v2, repaired policy) |
| Rationale | Local holdout favors Dragapult; ladder EV gap vs Starmie only **+3.7 pp**; Phase 3–5 require one policy stack |
| Holdout panel | **v2** — Phase 1 panel v1 + first-option stub numbers are not comparable |
