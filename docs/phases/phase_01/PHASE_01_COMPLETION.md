# Phase 1 — Completion checklist

**Status: COMPLETE offline for A/B/Merged; online A/B complete; Merged ladder metrics pending**

**Goal:** Working submission + reproducible offline evaluation harness.  
**Ablation starting points:** A = no search; B = search, no adaptation; **Merged (C)** = search + adaptation (V4-style).

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Submit Dragapult-only policy as **Baseline A** | **Done** | `main_baseline_a.py`; ladder peak **433** → ~**507** |
| 2 | Submit Dragapult + UCB1 as **Baseline B** | **Done** | `main_baseline_b.py`; ladder peak **612** → ~**507** |
| 3 | Record ladder ratings for A/B | **Done** | [`online/KAGGLE_LOG.md`](online/KAGGLE_LOG.md) |
| 4 | `run_holdout_suite()` vs Alakazam/Crustle/Spidops/Starmie | **Done** | [`offline/results/`](offline/results/) |
| 5 | Offline holdout for **Merged (C)** | **Done** | `main_baseline_merged.py`; pooled **41.9%** |
| 6 | Ladder ratings / replays for Merged | **Pending** | Submitted; fill when UI + JSON available |

---

## Deliverables checklist

### Code / harness

- [x] Baseline A / B / Merged agents flagged correctly
- [x] Holdout panel (4 archetypes)
- [x] `run_holdout_suite()` + `scripts/run_phase1_holdout.py` (supports `baseline_merged`)
- [x] Analyzers: `analyze_phase1_results.py`, `analyze_kaggle_match_logs.py`

### Offline results (fetched & documented)

Canonical: **40 games × 4 opponents × 3 baselines = 480 games**  
Source: [`offline/results/phase1_holdout_summary_latest.json`](offline/results/phase1_holdout_summary_latest.json)

| Baseline | Alakazam | Crustle | Spidops | Starmie | Pooled |
|----------|---------:|--------:|--------:|--------:|-------:|
| A | 20.0% | 77.5% | 85.0% | 82.5% | **66.2%** |
| B | 15.0% | 85.0% | 75.0% | 80.0% | **63.7%** |
| Merged | 2.5% | 30.0% | 75.0% | 60.0% | **41.9%** |

| Contrast | Δ |
|----------|--:|
| B − A (search) | −2.5 pp |
| Merged − B (adaptation) | **−21.9 pp** |
| Merged − A (full stack) | −24.4 pp |

Gates (≥52%): A fails Alakazam; B fails Alakazam; Merged fails **Alakazam + Crustle**.

**Validity:** These Phase 1 rates used the same `choose()` scoping bug later found in V1–V4. A/B/Merged here are first-option stubs on **panel v1**, not a search/adaptation ablation. Canonical repaired-policy numbers: Phase 2 Dragapult **83.1%**; Phase 3 V1 **90.0%**; Phase 4 best search **57.5%**; Phase 5 V3−V1 **−5.0 pp**.

### Online results

| Metric | A | B | Merged |
|--------|--:|--:|--------|
| Peak rating | 433 | 612 | *pending* |
| Equilibrium | ~507 | ~507 | *pending* |
| Logged replays | 9 | 10 | *pending* |

---

## Paper-facing interpretation

| Claim | Phase 1 support |
|-------|-----------------|
| Harness + ladder logging exists | **Yes** |
| Clean A vs B search ablation | **No** — both stubs; search never ran |
| Offline Merged is an adaptation result | **No** — same stub on panel v1 |
| A ≈ B at ~507 is a search null | **No** — two identical crash fallbacks on sample-water |
| Adaptation online vs ~507 | **Unknown** — Merged ratings not ingested; use Phase 3/5 offline instead |

Do not cite the B−A −2.5 pp or Merged −21.9 pp rows as component effects.

---

## Known caveats

1. Crustle/Spidops/Starmie = placeholder decks + random agents (panel v1).
2. All three offline rates are first-option stubs (`UnboundLocalError` in `choose()`).
3. Merged ladder ratings/replays not ingested.
4. Phase 1 ladder decks were sample-water, not Dragapult.

---

## Verdict

Phase 1 delivered the **holdout harness and ladder logging**. Its A/B/C numbers are historical stubs. Canonical component effects are Phases 3–5. Submission of record is repaired **V1 + Dragapult**.
