# Phase 1 — Completion checklist

**Status: COMPLETE** (with documented caveats below)

**Goal:** Working submission + reproducible offline evaluation harness.  
**Ablation starting points:** Baseline A = no search; Baseline B = search, no opponent adaptation.

---

## Research-plan tasks

| # | Task | Status | Evidence |
|---|------|--------|----------|
| 1 | Submit Dragapult-only policy as **Baseline A** (no search, no opponent detection) | **Done** | Agent: `notebooks/agents/main_baseline_a.py` (`USE_SEARCH=False`, `USE_OPPONENT_ADAPTATION=False`). Ladder rating **433**. Replays under `logs/phase1_logs/baseline_a/`. |
| 2 | Submit Dragapult + UCB1 Search as **Baseline B** | **Done** | Agent: `notebooks/agents/main_baseline_b.py` (`USE_SEARCH=True`, `USE_OPPONENT_ADAPTATION=False`). Ladder rating **612**. Replays under `logs/phase1_logs/baseline_b/`. |
| 3 | Record ladder ratings for both | **Done** | [`online/KAGGLE_LOG.md`](online/KAGGLE_LOG.md) — A **433**, B **612** (+179). |
| 4 | Implement `run_holdout_suite()` vs fixed panel (Alakazam, Crustle, Spidops, Starmie) | **Done** | `scripts/holdout_runner.py` → `kaggle_environments.make("cabt")` + `env.run`. Panel: `notebooks/holdout/panel/`. Results: [`offline/results/`](offline/results/). |

---

## Deliverables checklist

### Code / harness

- [x] Baseline A agent built and flagged correctly
- [x] Baseline B agent built and flagged correctly
- [x] Holdout panel dirs for all four archetypes (`deck.csv` + `main.py`)
- [x] `run_holdout_suite()` simulates real cabt games (not stubs)
- [x] CLI runner: `scripts/run_phase1_holdout.py`
- [x] Eval notebook: `notebooks/PHASE_01_BASELINE_EVAL.ipynb`
- [x] Offline analyzer: `scripts/analyze_phase1_results.py`
- [x] Online analyzer: `scripts/analyze_kaggle_match_logs.py`

### Offline results (fetched & documented)

Canonical run: **40 games × 4 opponents × 2 baselines = 320 games**  
Source of truth: [`offline/results/phase1_holdout_summary_latest.json`](offline/results/phase1_holdout_summary_latest.json)

| Baseline | Opponent | Win rate | Record | Gate (≥52%) |
|----------|----------|---------:|--------|-------------|
| A | alakazam | 20.0% | 8/40 | fail |
| A | crustle | 77.5% | 31/40 | pass |
| A | spidops | 85.0% | 34/40 | pass |
| A | starmie | 82.5% | 33/40 | pass |
| B | alakazam | 15.0% | 6/40 | fail |
| B | crustle | 85.0% | 34/40 | pass |
| B | spidops | 75.0% | 30/40 | pass |
| B | starmie | 80.0% | 32/40 | pass |

- **Pooled:** A 66.2% (106/160), B 63.7% (102/160), search Δ **−2.5 pp** offline  
- Written up: [`offline/HOLDOUT_LOG.md`](offline/HOLDOUT_LOG.md), [`offline/HOLDOUT_ANALYSIS.md`](offline/HOLDOUT_ANALYSIS.md)

### Online results (fetched & documented)

| Metric | Baseline A | Baseline B |
|--------|------------|------------|
| Ladder rating (early peak) | 433 | **612** (+179) |
| Ladder rating (equilibrium) | **~507** | **~507** (≈ null) |
| Downloaded replays (early window) | 9 (4W–5L, 44.4%) | 10 (5W–5L, 50.0%) |

**Convergence finding:** Search provided a placement advantage (+179) but did not sustain a differential at equilibrium — base policy evaluation is the binding constraint. Offline search null (−2.5 pp) is corroborated. Documented in [`online/KAGGLE_LOG.md`](online/KAGGLE_LOG.md).

- Written up: [`online/KAGGLE_LOG.md`](online/KAGGLE_LOG.md), [`online/KAGGLE_ANALYSIS.md`](online/KAGGLE_ANALYSIS.md), [`online/results/kaggle_log_analysis.json`](online/results/kaggle_log_analysis.json)

### Paper-facing interpretation

| Claim | Supported by Phase 1? |
|-------|------------------------|
| Clean A vs B ablation (search on/off, adaptation off) | **Yes** |
| Offline harness independent of ladder | **Yes** |
| Live ratings recorded for both | **Yes** (peak + equilibrium) |
| Search clearly wins offline overall | **No** — mixed (−2.5 pp pooled) |
| Search sustains online rating edge | **No** — converges to A ≈ B (~507) |
| Both struggle vs strong Alakazam-style play | **Yes** |
| Search-alone null strengthens Phase 3 story | **Yes** — if V4 lifts and V2 does not, adaptation is the mechanism |

---

## Known caveats (not blockers for Phase 1 close)

1. **Crustle / Spidops / Starmie** holdout decks + agents are **placeholders** (official sample deck + random agent). A vs B comparison remains valid on a fixed panel; absolute matchup rates for those three are directional only.
2. Ladder JSON replays are a **sample** of games behind each rating, not the full ladder history.
3. Opponent **identity** is not in replay files — only decks / board-visible cards.
4. Refresh ladder ratings in `online/KAGGLE_LOG.md` if they move before paper freeze.

---

## Optional follow-ups (post–Phase 1, not required to close)

- Replace placeholder opponent decks with field-accurate lists.
- Download more ladder replays and re-run `analyze_kaggle_match_logs.py`.
- Proceed to **Phase 2** (deck selection: Dragapult vs Starmie) using the same holdout harness.

---

## Verdict

**Phase 1 is complete.** All four research-plan tasks are done; offline and online results are observed and documented under `docs/phases/phase_01/`. Ready for Phase 2.
