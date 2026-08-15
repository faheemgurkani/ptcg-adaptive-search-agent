# Phase 3 — Completion checklist

**Status: COMPLETE (offline ablation on panel v2)**

**Goal:** Isolate search vs adaptation contributions (paper Table 1).

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Build V3 (adaptation only, no search) | **Done** | `main_baseline_v3.py` via `build_merged_agent.py` |
| 2 | Run V1–V4 vs panel v2 (40 games/matchup) | **Done** | `scripts/run_phase3_holdout.py` → [`offline/results/`](offline/results/) |
| 3 | Per-matchup win rates + component contrasts | **Done** | [`offline/HOLDOUT_ANALYSIS.md`](offline/HOLDOUT_ANALYSIS.md) |
| 4 | Crustle/stall vs search attribution | **Done** | V3−V1 Crustle **−7.5 pp** (adaptation hurt, not helped) |
| 5 | Document for paper §Experiments | **Done** | `conference_101719.tex` §Phase 3 |

---

## Verdict (offline, panel v2)

| Version | Pooled | vs V1 |
|---------|-------:|------:|
| V1 (policy) | **40.0%** | — |
| V2 (+ search) | 32.5% | −7.5 pp |
| V3 (+ adaptation) | 36.2% | −3.8 pp |
| V4 (full) | 34.4% | −5.6 pp |

**Neither search nor adaptation improves the committed Dragapult stack on this panel.** Search regresses most vs Starmie; adaptation regresses vs Crustle. V1 remains the strongest configuration offline. Online ladder validation (Phase 6) needed to test transfer.

---

## Caveats

- Panel v2; not comparable to Phase 1 ablation on panel v1.
- Crustle/Spidops/Starmie opponents still random-policy.
- Phase 2 deck-commitment submission (Baseline A) remains the Kaggle agent until Phase 6 promotes a stronger variant.
