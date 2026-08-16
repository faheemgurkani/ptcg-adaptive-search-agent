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

**Validity:** These Phase 1 rates used the same `choose()` scoping bug later found in V1–V4. A/B/Merged here are first-option stubs on **panel v1**, not a search/adaptation ablation. Canonical repaired-policy numbers live in Phase 2 (Dragapult 83.1%) and Phase 3 (V1 90.0%).

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
| Clean A vs B (search on/off) | **Yes** |
| Offline Merged (search + adaptation) measured | **Yes** — **negative** vs B on this panel |
| Search sustains ladder edge | **No** (A ≈ B ~507) |
| Adaptation breaks ~507 ceiling online | **Unknown** — awaiting Merged ladder |
| Adaptation helps offline on current panel | **No** (−21.9 pp vs B) |

---

## Known caveats

1. Crustle/Spidops/Starmie = placeholder decks + random agents.
2. Merged offline collapse (esp. Crustle 30%) may reflect miscalibrated adaptation on non-field decks — validate on ladder + better panels.
3. Merged ladder ratings/replays not yet ingested.

---

## Verdict

Phase 1 **offline harness + A/B/Merged holdout** is done. Online A/B documented with convergence. **Update this file when Merged ladder KPIs arrive**, then proceed to Phase 2.
