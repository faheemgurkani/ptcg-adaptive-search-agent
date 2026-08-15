# Phase 3 — Completion checklist

**Status: COMPLETE (offline ablation on panel v2)**

**Goal:** Isolate search vs adaptation contributions (paper Table 1 / `tab:phase3-ablation`).

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Build V3 (adaptation only, no search) | **Done** | `main_baseline_v3.py` via `build_merged_agent.py` |
| 2 | Run V1–V4 vs panel v2 (40 games/matchup) | **Done** | `scripts/run_phase3_holdout.py` → [`offline/results/`](offline/results/) |
| 3 | Per-matchup win rates + all component contrasts | **Done** | [`offline/HOLDOUT_ANALYSIS.md`](offline/HOLDOUT_ANALYSIS.md) · [`PHASE_03_RESULTS.json`](PHASE_03_RESULTS.json) |
| 4 | Crustle/stall adaptation hypothesis test | **Done** | V3−V1 Crustle **−7.5 pp** (hypothesis **fails**) |
| 5 | Starmie/search tactical hypothesis test | **Done** | V2−V1 Starmie **−20.0 pp** (search **hurts**) |
| 6 | Document for paper §Phase 3 + figures | **Done** | `conference_101719.tex` · `fig_phase3_*.pdf` |

---

## Verdict (offline, panel v2)

| Version | Pooled (record) | vs V1 |
|---------|----------------:|------:|
| **V1 (policy)** | **40.0%** (64/160) | — |
| V2 (+ search) | 32.5% (52/160) | −7.5 pp |
| V3 (+ adaptation) | 36.2% (58/160) | −3.8 pp |
| V4 (full) | 34.4% (55/160) | −5.6 pp |

**Neither search nor adaptation improves the committed Dragapult stack.** V1 remains strongest offline. Interaction effects (V4−V2, V4−V3) are only ±1.9 pp. All versions fail vs Alakazam.

**Interim research answer:** Adaptive search does **not** beat static policy on this panel offline. Phase 2 Kaggle submission (Baseline A / V1) remains the correct agent.

---

## Cross-phase (do not merge tables)

| Version | Phase 1 pool (panel v1) | Phase 3 pool (panel v2) |
|---------|------------------------:|------------------------:|
| V1 | 66.2% | 40.0% |
| V2 | 63.7% | 32.5% |
| V4 | 41.9% | 34.4% |
| V3 | *(not measured)* | 36.2% |

Panel upgrade dominates cross-phase deltas.

---

## Caveats

- Panel v2; Crustle/Spidops/Starmie opponents still random-policy.
- Phase 2 deck-selection V1 run: 38.8% pooled (same policy, run variance vs Phase 3 canonical 40.0%).
- Phase 5 will deepen adaptation attribution (detector timing, false positives); Phase 6 tests ladder transfer.
