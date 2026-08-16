# Phase 2 — Completion checklist

**Status: COMPLETE** (re-run after `choose()` scoping fix)

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

Canonical re-run (repaired `DragapultPolicy`, panel v2, 40 games/matchup): Dragapult **83.1%** (133/160) vs Starmie heuristic **58.8%** (94/160). Usage-weighted edge: Dragapult **+19.9 pp**, Starmie **−13.2 pp**. Ladder EV still favors Starmie by only **+3.7 pp** (53.1% vs 49.5%). Commitment is now aligned with both local holdout and Phase 3–5 policy-stack continuity.

A pre-fix Phase 2 run (38.8% vs 54.4%) measured first-option fallback after `UnboundLocalError` in `choose()` — **superseded**. Do not cite 38.8%/54.4% as deck-selection evidence.

## Panel / validity notes

- Phase 1 used **panel v1** and the same broken `choose()` (first-option stub). Phase 1 **66.2%** is not a working Dragapult policy.
- Phase 2+ uses **panel v2**. Compare only repaired-policy runs to each other (Phase 2 Dragapult 83.1% vs Phase 3 V1 90.0% is seed/cabt-shuffle variance on the same stack).
