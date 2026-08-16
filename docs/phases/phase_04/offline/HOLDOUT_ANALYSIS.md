# Phase 4 holdout analysis — search depth

Panel **v2**, committed **Dragapult**, agent **V2** (UCB1 on, adaptation off).
Paired seeds (`md5(opponent:game_idx)`). `choose()` must succeed.

## Cells

| Cell | Candidates | Time (s) | Alakazam | Crustle | Spidops | Starmie | **Pooled** | Record |
|------|----------:|---------:|---------:|--------:|--------:|--------:|-----------:|--------|
| `c8_t500` | 8 | 0.5 | 5.0% | 50.0% | 45.0% | 50.0% | **37.5%** | 60/160 |
| `c8_t1000` | 8 | 1.0 | 0.0% | 47.5% | 50.0% | 42.5% | **35.0%** | 56/160 |
| `c4_t1500` | 4 | 1.5 | 5.0% | 75.0% | 82.5% | 67.5% | **57.5%** | 92/160 |
| `c8_t1500` | 8 | 1.5 | 7.5% | 57.5% | 40.0% | 50.0% | **38.8%** | 62/160 |
| `c12_t1500` | 12 | 1.5 | 5.0% | 37.5% | 30.0% | 17.5% | **22.5%** | 36/160 |
| `c16_t1500` | 16 | 1.5 | 2.5% | 47.5% | 17.5% | 40.0% | **26.9%** | 43/160 |
| `c8_t2000` | 8 | 2.0 | 2.5% | 45.0% | 35.0% | 25.0% | **26.9%** | 43/160 |

Phase 3 anchors (not re-run): V1 **90.0%**; V2 at 0.3 s / 8 candidates **36.2%**.

## Time curve (8 candidates)

| Time (s) | Pooled |
|---------:|-------:|
| 0.5 | 37.5% |
| 1.0 | 35.0% |
| 1.5 | 38.8% |
| 2.0 | 26.9% |

**Knee:** 0.5 s (within 2 pp of best).

## Candidate curve (1.5 s)

| Candidates | Pooled |
|-----------:|-------:|
| 4 | 57.5% |
| 8 | 38.8% |
| 12 | 22.5% |
| 16 | 26.9% |

**Knee:** 4 candidates (within 2 pp of best).

## Findings

- Best search cell c4_t1500 at 57.5% pooled (-32.5 pp vs Phase 3 V1 90.0%).
- Time-budget knee (8 candidates): 0.5 s — within 2 pp of best.
- Candidate-count knee (1.5 s): 4 — within 2 pp of best.
- No searched configuration approaches the no-search V1 baseline.

## Paper

This is Figure 2 (win rate vs compute). Do not mix with Phase 3 V2 0.3 s except as a labeled reference.

