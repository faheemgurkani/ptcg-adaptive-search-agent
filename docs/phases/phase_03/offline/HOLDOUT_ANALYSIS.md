# Phase 3 — Ablation analysis (panel v2, committed Dragapult deck)

**Status:** complete · **640 games** · deck: `data/decks/dragapult.csv` · panel: **v2**

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
| alakazam | 7.5% (3/40) | 5.0% (2/40) | 5.0% (2/40) | 2.5% (1/40) | -2.5% | -2.5% | -2.5% | -2.5% |
| crustle | 27.5% (11/40) | 27.5% (11/40) | 20.0% (8/40) | 27.5% (11/40) | +0.0% | -7.5% | +0.0% | +7.5% |
| spidops | 72.5% (29/40) | 65.0% (26/40) | 70.0% (28/40) | 67.5% (27/40) | -7.5% | -2.5% | +2.5% | -2.5% |
| starmie | 52.5% (21/40) | 32.5% (13/40) | 50.0% (20/40) | 40.0% (16/40) | -20.0% | -2.5% | +7.5% | -10.0% |

## Pooled summary (160 games per version)

| Version | Record pool | Equal-weight pool | Gate failures |
|---------|------------:|------------------:|---------------|
| V1 | 40.0% (64/160) | 40.0% | alakazam, crustle |
| V2 | 32.5% (52/160) | 32.5% | alakazam, crustle, starmie |
| V3 | 36.2% (58/160) | 36.2% | alakazam, crustle, starmie |
| V4 | 34.4% (55/160) | 34.4% | alakazam, crustle, starmie |

## Component contrasts (pooled, pp)

| Contrast | Δ (pp) |
|----------|-------:|
| Search (V2 − V1) | -7.5 |
| Adaptation (V3 − V1) | -3.8 |
| Adaptation on search (V4 − V2) | +1.9 |
| Search on adaptation (V4 − V3) | -1.9 |
| Full stack (V4 − V1) | -5.6 |

## Hypothesis tests

- **Crustle/stall (adaptation):** V3 − V1 = -7.5 pp (27.5% → 20.0%) — **hypothesis fails**
- **Starmie (search / tactical):** V2 − V1 = -20.0 pp (52.5% → 32.5%) — search **hurts**
- **Alakazam (rule-based):** all versions ≤7.5%; V4 worst at 2.5%

## Cross-phase reference (panel v1 vs v2 — not directly comparable)

| Version | Phase 1 pool (v1) | Phase 3 pool (v2) | Δ (v2−v1 panel)* |
|---------|------------------:|------------------:|-----------------:|
| V1 | 66.2% | 40.0% | -26.2 pp |
| V2 | 63.7% | 32.5% | -31.2 pp |
| V4 | 41.9% | 34.4% | -7.5 pp |

*Delta reflects panel upgrade + run variance, not agent regression in isolation.

## Research question (interim answer)

> Does opponent-adaptive heuristic search outperform a static rule-based policy?

**On panel v2 offline: No.** V1 (static policy) beats V2, V3, and V4 on pooled win rate. Search and adaptation each **reduce** performance; the Crustle adaptation hook is counterproductive. Online ladder shows A≈B at ~507 (null search effect), consistent with offline search regression.

## Findings summary

- V1 (pure policy) is the strongest offline configuration on panel v2 (40.0% pooled).
- Search (V2−V1) hurts pooled performance by 7.5 pp; largest regression vs Starmie (−20.0 pp).
- Adaptation alone (V3−V1) hurts pooled by 3.8 pp; Crustle/stall hypothesis fails (−7.5 pp).
- Full system V4 (34.4% pooled) does not beat V1; interaction effects (V4−V2, V4−V3) are ±1.9 pp.
- All versions fail vs Alakazam (rule-based opponent).
- Phase 1 panel v1 numbers are not comparable; cross-phase deltas reflect panel hardness change.
- Kaggle submission remains Phase 2 commitment: Baseline A (V1) + Dragapult deck.

## Caveats

- Panel **v2**; not comparable to Phase 1 panel v1 without explicit labeling.
- Crustle/Spidops/Starmie opponents use random agents; Alakazam is rule-based.
- Phase 2 deck-selection run reported Dragapult at 38.8% pooled (same V1 policy); Phase 3 canonical ablation run: **40.0%** — run-to-run variance on panel v2.
- Phase 1 Merged C (early V4) on panel v1: 41.9% — not comparable to Phase 3 V4 (34.4% on v2).
