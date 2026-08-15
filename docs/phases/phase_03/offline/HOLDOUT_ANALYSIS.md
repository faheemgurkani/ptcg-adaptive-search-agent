# Phase 3 — Ablation analysis (panel v2, committed Dragapult deck)

## Ablation matrix (2×2)

| Version | Search | Adaptation | Role |
|---------|:------:|:----------:|------|
| V1 | ✗ | ✗ | Pure Dragapult baseline |
| V2 | ✓ | ✗ | Search contribution |
| V3 | ✗ | ✓ | Adaptation contribution |
| V4 | ✓ | ✓ | Full system |

## Win rate by matchup (40 games each)

| Opponent | V1 (policy only) | V2 (+ search) | V3 (+ adaptation) | V4 (full) | V2−V1 | V3−V1 | V4−V2 | V4−V3 |
|----------|-------:|-------:|-------:|-------:|------:|------:|------:|------:|
| alakazam | 7.5% (3/40) | 5.0% (2/40) | 5.0% (2/40) | 2.5% (1/40) | -2.5% | -2.5% | -2.5% | -2.5% |
| crustle | 27.5% (11/40) | 27.5% (11/40) | 20.0% (8/40) | 27.5% (11/40) | +0.0% | -7.5% | +0.0% | +7.5% |
| spidops | 72.5% (29/40) | 65.0% (26/40) | 70.0% (28/40) | 67.5% (27/40) | -7.5% | -2.5% | +2.5% | -2.5% |
| starmie | 52.5% (21/40) | 32.5% (13/40) | 50.0% (20/40) | 40.0% (16/40) | -20.0% | -2.5% | +7.5% | -10.0% |

## Pooled (160 games per version)

- **V1 (policy only):** 40.0% (64/160)
- **V2 (+ search):** 32.5% (52/160)
- **V3 (+ adaptation):** 36.2% (58/160)
- **V4 (full):** 34.4% (55/160)

- **Search effect (V2 − V1):** -7.5%
- **Adaptation effect (V3 − V1):** -3.8%
- **Adaptation on search (V4 − V2):** +1.9%
- **Search on adaptation (V4 − V3):** -1.9%
- **Full stack (V4 − V1):** -5.6%

## Component attribution highlights

- **Crustle/stall (adaptation hypothesis):** V3 − V1 = -7.5% (V1 27.5% → V3 20.0%)
- **Alakazam (tactical/search signal):** V2 − V1 = -2.5% (V1 7.5% → V2 5.0%)

## Holdout gates (≥52% per matchup)

- **V1 (policy only)** fails vs: alakazam, crustle
- **V2 (+ search)** fails vs: alakazam, crustle, starmie
- **V3 (+ adaptation)** fails vs: alakazam, crustle, starmie
- **V4 (full)** fails vs: alakazam, crustle, starmie

## Caveats

- Panel **v2** (upgraded Crustle/Spidops/Starmie decks); not comparable to Phase 1 panel v1 numbers.
- Crustle/Spidops/Starmie opponents use random agents; Alakazam is rule-based.
- Phase 1 early V4 (Merged C) was measured on panel v1; Phase 3 V4 re-runs on panel v2.
