# Phase 1 — Online Kaggle log

**Validity:** A/B ladder submissions were the silent `choose()` stub on the **sample-water** deck (Wugtrio 721–723), not a working Dragapult policy and not a search ablation. Equilibrium ~507 is two identical fallbacks. Do **not** use these ratings as Phase 6 transfer for repaired V1.

**Phase 1 status:** A/B complete online; Merged (C) submitted with ratings/replays still not ingested — [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).

## Submissions and ratings

| Baseline | What actually ran | Early peak | Equilibrium | Status |
|----------|-------------------|----------:|------------:|--------|
| baseline_a | First-option stub (sample water) | **433** | **~507** | Submitted |
| baseline_b | Same stub (search never started) | **612** | **~507** | Submitted |
| baseline_merged (C) | Same crash + adaptation flags | *TBD* | *TBD* | Submitted; logs not ingested |

Ratings come from the Kaggle UI — they are **not** embedded in replay JSON files.

### Ladder convergence (A/B)

Both A and B **converged to ~507** after placement. That is the expected outcome if both agents are the same first-option stub.

The early **+179** peak gap is a cold-start / matchmaking artifact (B punching down during placement), not a measured UCB1 effect.

Canonical search measurement is Phase 3 V2−V1 (**−53.8 pp**) after the `choose()` fix, not this ladder pair.

### Merged (Baseline C)

Offline Merged on panel v1 is a **stub** (pooled 41.9%). Do not treat that as an adaptation result. Canonical adaptation is Phase 3/5 V3−V1 (**−5.0 pp**).

When available, add:
- Peak / equilibrium ladder rating
- Replay JSONs under `logs/phase1_logs/baseline_merged/{won,lost}/`

## Logged replay sample (early / mid window) — A/B only

| Baseline | Logged replays | W–L | Logged win rate |
|----------|---------------:|----:|----------------:|
| baseline_a | 9 | 4–5 | 44.4% |
| baseline_b | 10 | 5–5 | 50.0% |
| baseline_merged | *pending* | — | — |

## Replay layout

```
logs/phase1_logs/
  baseline_a/{won,lost}/<episode_id>.json
  baseline_b/{won,lost}/<episode_id>.json
  baseline_merged/{won,lost}/<episode_id>.json   # add when downloaded
```

```bash
python scripts/analyze_kaggle_match_logs.py \
  --rating baseline_a=507 --rating baseline_b=507
```

| File | Description |
|------|-------------|
| [KAGGLE_ANALYSIS.md](KAGGLE_ANALYSIS.md) | Downloaded A/B episode tables (stub submissions) |
| [results/kaggle_log_analysis.json](results/kaggle_log_analysis.json) | Machine-readable stats |

Offline holdout (also stub): [../offline/HOLDOUT_LOG.md](../offline/HOLDOUT_LOG.md).
