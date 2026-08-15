# Phase 2 — Deck selection & meta analysis

**Status: COMPLETE** — committed deck: **Dragapult**

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
| Agent stack | `DragapultPolicy` (Baseline A/B / V1–V4) |
| Rationale | Ladder EV gap vs Starmie only **+3.7pp**; local Starmie lead is agent-asymmetric; Phase 3–5 require one policy stack |
| Holdout panel | **v2** (upgraded Crustle/Spidops/Starmie decks) — not comparable to Phase 1 panel v1 numbers |
