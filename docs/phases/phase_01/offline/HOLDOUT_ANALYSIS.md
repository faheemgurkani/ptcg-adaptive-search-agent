# Phase 1 holdout analysis

## Win rate by matchup (40 games each)

| Opponent | Baseline A | Baseline B | B − A | Search helped? |
|----------|------------|------------|-------|----------------|
| alakazam | 20.0% (8/40) | 15.0% (6/40) | -5.0% | no |
| crustle | 77.5% (31/40) | 85.0% (34/40) | +7.5% | yes |
| spidops | 85.0% (34/40) | 75.0% (30/40) | -10.0% | no |
| starmie | 82.5% (33/40) | 80.0% (32/40) | -2.5% | no |

## Overall (all opponents pooled)

- **Baseline A:** 66.2% (106/160)
- **Baseline B:** 63.7% (102/160)
- **Search net change:** -2.5%

## Holdout gates (≥52% per matchup)

- **A (no search)** fails vs: alakazam
- **B (+ search)** fails vs: alakazam

## What this means

- **Alakazam** uses a real rule-based opponent; low win rates there are the most meaningful signal.
- **Crustle / Spidops / Starmie** still use placeholder decks + random agent — treat those numbers as directional only.
- Search is mixed or negative overall offline (−2.5 pp pooled).

### Online corroboration (ladder convergence)

The offline null should be taken seriously: on the live ladder, A and B both converged to **~507** after an early B peak of 612 vs A 433 (+179). Search alone did not sustain a rating differential. Binding constraint appears to be the **base policy evaluation**, not search depth. See [`../online/KAGGLE_LOG.md`](../online/KAGGLE_LOG.md).

This is a gift for Phase 3: V1 ≈ V2 at equilibrium is a clean search-alone null; if V4 lifts and V2 does not, adaptation is the mechanism.

## Next steps

1. ~~**Kaggle:** submit Baseline A/B and log ratings~~ — done (peak A 433 / B 612; equilibrium ~507 each).
2. Optional: post-convergence search-override diagnostic on B’s recent replays.
3. **Optional:** replace placeholder opponent decks under `notebooks/holdout/panel/`.
4. **Phase 2:** deck selection (Dragapult vs Starmie) using the same holdout harness.

Phase 1 close-out: [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).
