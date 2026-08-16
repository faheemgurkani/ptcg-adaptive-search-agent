# Phase 3 — Completion checklist

**Status: COMPLETE** (offline ablation on panel v2; **re-run after `choose()` fix**)

**Goal:** Isolate search vs adaptation contributions (paper Table 1 / `tab:phase3-ablation`).

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Build V3 (adaptation only, no search) | **Done** | `main_baseline_v3.py` via `build_merged_agent.py` |
| 2 | Run V1–V4 vs panel v2 (40 games/matchup) | **Done** | `scripts/run_phase3_holdout.py` → [`offline/results/`](offline/results/) |
| 3 | Per-matchup win rates + all component contrasts | **Done** | [`offline/HOLDOUT_ANALYSIS.md`](offline/HOLDOUT_ANALYSIS.md) · [`PHASE_03_RESULTS.json`](PHASE_03_RESULTS.json) |
| 4 | Crustle/stall adaptation hypothesis test | **Done** | V3−V1 Crustle **−15.0 pp** (hypothesis **fails**) |
| 5 | Starmie/search tactical hypothesis test | **Done** | V2−V1 Starmie **−62.5 pp** (search **hurts**; search actually executed) |
| 6 | Document for paper §Phase 3 + figures | **Done** | `conference_101719.tex` · `fig_phase3_*.pdf` |

---

## Verdict (offline, panel v2, repaired policy)

| Version | Pooled (record) | vs V1 |
|---------|----------------:|------:|
| **V1 (policy)** | **90.0%** (144/160) | — |
| V3 (+ adaptation) | 85.0% (136/160) | −5.0 pp |
| V2 (+ search) | 36.2% (58/160) | −53.8 pp |
| V4 (full) | 34.4% (55/160) | −55.6 pp |

`choose_fail=0` on all four variants. Search ran (`search_ok` 1.75M / 2.10M on V2 / V4). V1 passes every holdout gate except the 52% line on Alakazam is not required (Alakazam **65%**, pass). V2/V4 fail most gates.

**Neither search nor adaptation improves the repaired Dragapult policy.** V1 remains strongest offline. Kaggle submission: **V1 + Dragapult**.

A pre-fix Phase 3 table (V1 40.0% / V2 32.5% / V3 36.2% / V4 34.4%) measured first-option fallback — **superseded**. Those CIs overlapped because the policy never ran.

**Interim research answer:** Adaptive search does **not** beat the static policy on this panel once `choose()` actually executes. Search is a large regression (−53.8 pp). Adaptation is a small regression (−5.0 pp; Crustle −15.0 pp).

---

## Cross-phase (do not merge tables)

| Version | Phase 1 pool (panel v1, stub) | Phase 3 pre-fix (v2, stub) | Phase 3 **canonical** (v2, repaired) |
|---------|------------------------------:|---------------------------:|-------------------------------------:|
| V1 | 66.2% | 40.0% | **90.0%** |
| V2 | 63.7% | 32.5% | 36.2% |
| V3 | *(not measured)* | 36.2% | 85.0% |
| V4 | 41.9% | 34.4% | 34.4% |

Phase 1 and pre-fix Phase 3 are first-option stubs. Canonical Phase 3 is the first valid 2×2 ablation.

---

## Caveats

- Panel v2; Crustle/Spidops/Starmie opponents still random-policy; Alakazam is rule-based.
- Holdout search budget: `PTCG_SEARCH_TIME_BUDGET=0.3` s (submission default remains 1.5 s).
- Seeds: `md5(opponent:game_idx)` shared across variants; cabt C++ shuffle may still be unseeded.
- Phase 2 Dragapult 83.1% vs Phase 3 V1 90.0%: same stack, different seed namespace + unseeded engine.
- Phase 4 (complete): extra UCB1 compute does not recover V1 (best 57.5% at 4 cand / 1.5 s).
- Phase 5 (offline complete): V3−V1 **−5.0 pp** pooled, Crustle **−15.0 pp**; no extra detector; traces deferred.
- Phase 6: V1 package ready; live repaired-V1 transfer still pending. Submission stays **V1 + Dragapult**.
