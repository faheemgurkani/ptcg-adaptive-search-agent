# Phase 2 — Completion checklist

**Status: COMPLETE**

**Goal:** Commit to one deck with meta-informed justification before Phase 3.

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Holdout with Dragapult and Starmie vs four archetypes | **Done** | `scripts/run_phase2_holdout.py` → [`offline/results/`](offline/results/) |
| 2 | Record win rates per matchup | **Done** | Tables in [`offline/HOLDOUT_LOG.md`](offline/HOLDOUT_LOG.md) |
| 3 | Apply meta snapshot logic (usage share vs score rate) | **Done** | `scripts/meta_snapshot.py` + weighted edge in analysis |
| 4 | Document deck selection decision (paper §2) | **Done** | [`DECK_SELECTION_DECISION.json`](DECK_SELECTION_DECISION.json), paper section updated |
| 5 | Commit one deck before Phase 3 | **Done** | **Dragapult** → `data/deck.csv` ([`DECK_COMMITMENT.json`](DECK_COMMITMENT.json)) |

---

## Verdict

**Committed deck: Dragapult.**

Local holdout favors Starmie on equal-weight and usage-weighted scores, but the Starmie pilot is a thin heuristic while Dragapult uses the full `DragapultPolicy`. Ladder EV (equal-pilot field data) favors Starmie by only **+3.7pp** (< 5pp threshold). Commitment prioritizes a single policy stack for Phase 3–5 ablations; Starmie's local lead is retained as a sensitivity finding.
