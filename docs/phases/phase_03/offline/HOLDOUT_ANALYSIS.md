# Phase 3 — Ablation analysis (panel v2, committed Dragapult deck)

**Status:** complete · **640 games** · deck: `data/decks/dragapult.csv` · panel: **v2** · **repaired `choose()`**

## Ablation matrix (2×2)

| Version | Search | Adaptation | Agent file | Role |
|---------|:------:|:----------:|------------|------|
| V1 | ✗ | ✗ | `notebooks/agents/main_baseline_a.py` | Pure Dragapult baseline |
| V2 | ✓ | ✗ | `notebooks/agents/main_baseline_b.py` | Search contribution |
| V3 | ✗ | ✓ | `notebooks/agents/main_baseline_v3.py` | Adaptation contribution |
| V4 | ✓ | ✓ | `notebooks/agents/main_baseline_merged.py` | Full system |

## Table 1 — Win rate by matchup (40 games each)

| Opponent | V1 | V2 | V3 | V4 | V2−V1 | V3−V1 | V4−V2 | V4−V3 |
|----------|-----:|-----:|-----:|-----:|------:|------:|------:|------:|
| alakazam | 65.0% (26/40) | 5.0% (2/40) | 60.0% (24/40) | 5.0% (2/40) | -60.0% | -5.0% | +0.0% | -55.0% |
| crustle | 97.5% (39/40) | 52.5% (21/40) | 82.5% (33/40) | 47.5% (19/40) | -45.0% | -15.0% | -5.0% | -35.0% |
| spidops | 97.5% (39/40) | 50.0% (20/40) | 100.0% (40/40) | 37.5% (15/40) | -47.5% | +2.5% | -12.5% | -62.5% |
| starmie | 100.0% (40/40) | 37.5% (15/40) | 97.5% (39/40) | 47.5% (19/40) | -62.5% | -2.5% | +10.0% | -50.0% |

## Pooled summary (160 games per version)

| Version | Record pool | Equal-weight pool | Gate failures |
|---------|------------:|------------------:|---------------|
| V1 | 90.0% (144/160) | 90.0% | none |
| V2 | 36.2% (58/160) | 36.3% | alakazam, spidops, starmie |
| V3 | 85.0% (136/160) | 85.0% | none |
| V4 | 34.4% (55/160) | 34.4% | alakazam, crustle, spidops, starmie |

## Component contrasts (pooled, pp)

| Contrast | Δ (pp) |
|----------|-------:|
| Search (V2 − V1) | -53.8 |
| Adaptation (V3 − V1) | -5.0 |
| Adaptation on search (V4 − V2) | -1.9 |
| Search on adaptation (V4 − V3) | -50.6 |
| Full stack (V4 − V1) | -55.6 |

## Hypothesis tests

- **Crustle/stall (adaptation):** V3 − V1 = -15.0 pp (97.5% → 82.5%) — **hypothesis fails**
- **Starmie (search / tactical):** V2 − V1 = -62.5 pp (100.0% → 37.5%) — search **hurts**
- **Alakazam (rule-based):** V1 65.0%, V2 5.0%, V3 60.0%, V4 5.0%

## Cross-phase reference (panel v1 vs v2 — not directly comparable)

| Version | Phase 1 pool (v1) | Phase 3 pool (v2) | Δ (v2−v1 panel)* |
|---------|------------------:|------------------:|-----------------:|
| V1 | 66.2% | 90.0% | +23.8 pp |
| V2 | 63.7% | 36.2% | -27.5 pp |
| V4 | 41.9% | 34.4% | -7.5 pp |

*Delta reflects panel upgrade + run variance, not agent regression in isolation.

## Research question (interim answer)

> Does opponent-adaptive heuristic search outperform a static rule-based policy?

**On panel v2 offline (repaired policy):** V1 leads at 90.0% pooled. Search does not improve on the repaired policy. Adaptation does not improve on the repaired policy. Phase 4: extra search compute still does not recover V1 (best 57.5%).

## Findings summary

- V1 is the strongest offline configuration on panel v2 (90.0% pooled, 144/160).
- Search (V2−V1) is -53.8 pp pooled.
- Adaptation (V3−V1) is -5.0 pp pooled; Crustle -15.0 pp.
- Full stack (V4−V1) is -55.6 pp pooled.
- Alakazam remains the hardest cell (V1 65.0%).
- choose() now runs (POLICY_CHOOSE_FAIL=0); Phase 1–3 stub numbers are not comparable.
- Kaggle submission: strongest offline variant + Dragapult deck (Phase 4 left this unchanged).

## Caveats

- Panel **v2**; Phase 1 panel v1 used sample-water stand-ins and is not comparable.
- Crustle/Spidops/Starmie opponents use random agents; Alakazam is rule-based.
- `choose()` scoping is fixed; POLICY_CHOOSE_FAIL=0 on this run. Pre-fix 35–40% numbers were first-option stubs.
- Holdout search budget is `PTCG_SEARCH_TIME_BUDGET` (0.3s); submission default remains 1.5s.
