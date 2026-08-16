# Phase 5 — Adaptation analysis

Source: Phase 3 V1 vs V3, panel v2, repaired `choose()`. 40 games per matchup. No new holdout.

## V1 vs V3 (the Crustle test)

| Opponent | V1 | V3 | V3−V1 |
|----------|----|----|------:|
| Alakazam | 65.0% (26/40) | 60.0% (24/40) | −5.0 pp |
| **Crustle** | **97.5% (39/40)** | **82.5% (33/40)** | **−15.0 pp** |
| Spidops | 97.5% (39/40) | 100.0% (40/40) | +2.5 pp |
| Starmie | 100.0% (40/40) | 97.5% (39/40) | −2.5 pp |
| **Pooled** | **90.0% (144/160)** | **85.0% (136/160)** | **−5.0 pp** |

The Crustle-aware hook is a **forced switch off Budew** when Dwebble/Crustle `{344,345}` is in play. That is the intended stall read, and it is where adaptation hurts most.

The water hook is **+8000 energy-attach score** on Dragapult-ex when a water ID is visible. Starmie is the intended true-positive (`{360,361,1030,1031}` in the panel list) and still −2.5 pp.

## Detector false positives

`_opponent_is_water_deck` / `_opponent_is_crustle_wall` call `_opponent_has` on **active + bench**. They never inspect the hidden hand.

- Empty bench and empty matching active → **False**. Early game with no evolved/basic of those lines in play is a **false negative**, not a false positive.
- Panel list overlap: Alakazam none; Crustle only crustle IDs; Spidops none; Starmie only water IDs. No cross-archetype list contamination.

Per-decision “when did it first fire?” traces were **not** logged in Phase 3. That needs an instrumented rerun.

## Decision: no extra detector

We did **not** add Spidops or Festival detection.

Adaptation already fails its primary hypothesis (Crustle −15.0 pp). Spidops V3 is already 40/40 without a dedicated hook. Expanding a component that reduces win rate would not be a measured contribution.

## Submission

Keep `USE_OPPONENT_ADAPTATION=False` (V1).
