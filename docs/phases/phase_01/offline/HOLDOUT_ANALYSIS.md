# Phase 1 holdout analysis

## Win rate by matchup (40 games each)

| Opponent | A | B | Merged | B − A | Merged − B |
|----------|-------:|-------:|-------:|------:|----------:|
| alakazam | 20.0% (8/40) | 15.0% (6/40) | 2.5% (1/40) | -5.0% | -12.5% |
| crustle | 77.5% (31/40) | 85.0% (34/40) | 30.0% (12/40) | +7.5% | -55.0% |
| spidops | 85.0% (34/40) | 75.0% (30/40) | 75.0% (30/40) | -10.0% | +0.0% |
| starmie | 82.5% (33/40) | 80.0% (32/40) | 60.0% (24/40) | -2.5% | -20.0% |

## Overall (all opponents pooled)

- **A (no search):** 66.2% (106/160)
- **B (+ search):** 63.7% (102/160)
- **Merged / C (+ search + adaptation):** 41.9% (67/160)
- **Search net (B − A):** -2.5%
- **Adaptation net (Merged − B):** -21.9%
- **Full stack net (Merged − A):** -24.4%

## Holdout gates (≥52% per matchup)

- **A (no search)** fails vs: alakazam
- **B (+ search)** fails vs: alakazam
- **Merged / C (+ search + adaptation)** fails vs: alakazam, crustle

## What this means

- **Alakazam** uses a real rule-based opponent; low win rates there are the most meaningful signal.
- **Crustle / Spidops / Starmie** still use placeholder decks + random agent — treat those numbers as directional only.
- **Merged (Baseline C)** = search + opponent adaptation; offline KPIs below pair with pending ladder logs.
- Adaptation did not improve pooled holdout vs Baseline B in this panel.

## Next steps

1. ~~Baselines A/B offline + ladder~~ — see `docs/phases/phase_01/`.
2. Record merged agent ladder ratings / replays when available (`online/KAGGLE_LOG.md`).
3. **Optional:** replace placeholder opponent decks under `notebooks/holdout/panel/`.
4. **Phase 2:** deck selection (Dragapult vs Starmie) using the same holdout harness.

Phase 1 close-out: `docs/phases/phase_01/PHASE_01_COMPLETION.md`.
