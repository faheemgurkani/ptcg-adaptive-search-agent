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
- **Crustle / Spidops / Starmie** used **panel v1** (official sample deck + random agent) for this Phase 1 run — treat those matchup numbers as directional only.
- **Merged (Baseline C)** = search + opponent adaptation; offline KPIs below pair with pending ladder logs.
- Adaptation did not improve pooled holdout vs Baseline B in this panel.

## Panel version note (Phase 1 vs Phase 2)

Phase 1 canonical results above were collected on **holdout panel v1** (placeholder Crustle/Spidops/Starmie decks). Phase 2 upgraded opponent lists to **panel v2** (ladder Crustle; constructed Spidops/Starmie) before deck-selection runs.

**Do not compare Phase 1 and Phase 2 win rates directly.** Example: Baseline A pooled **66.2%** (Phase 1, panel v1) vs Dragapult **38.8%** (Phase 2, same `DragapultPolicy`, panel v2) — the drop reflects a harder panel, not a weaker agent. Within-phase contrasts (A vs B vs Merged; Dragapult vs Starmie) remain valid.

See [`../../phase_02/offline/HOLDOUT_LOG.md`](../../phase_02/offline/HOLDOUT_LOG.md) for panel v2 results.

## Next steps

1. ~~Baselines A/B offline + ladder~~ — see `docs/phases/phase_01/`.
2. Record merged agent ladder ratings / replays when available (`online/KAGGLE_LOG.md`).
3. ~~Replace placeholder opponent decks under `notebooks/holdout/panel/`~~ — done for Phase 2 (panel v2).
4. ~~**Phase 2:** deck selection (Dragapult vs Starmie)~~ — complete; committed **Dragapult** (`docs/phases/phase_02/`).

Phase 1 close-out: `docs/phases/phase_01/PHASE_01_COMPLETION.md`.
