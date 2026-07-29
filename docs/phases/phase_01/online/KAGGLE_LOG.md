# Phase 1 — Online Kaggle log

Live ladder submissions and downloaded replay analysis.

**Phase 1 status:** complete — see [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).

## Submissions and ratings

| Baseline | Agent | Early peak | Equilibrium | Status |
|----------|-------|----------:|------------:|--------|
| baseline_a | Dragapult, no search | **433** | **~507** | Submitted |
| baseline_b | Dragapult + UCB1 search | **612** | **~507** | Submitted |

Ratings come from the Kaggle UI — they are **not** embedded in replay JSON files.

### Ladder convergence (documented finding)

Both agents **converged to ~507** after the initial placement transient.

**What this means:** Matchmaking pairs agents near their current rating. B’s early +179 lead was partly cold-start / punching-down during placement and partly a narrow search edge that did not survive once both faced the same field at the same tier.

**Implications:**
1. The **floor (~507)** is the signal, not the early gap — Dragapult base policy evaluation is the binding constraint; search alone cannot climb past it.
2. Offline search null (−2.5 pp pooled; B worse vs Alakazam) is **corroborated** online — UCB1 as configured is not a reliable win-rate lift (likely optimizing a weak evaluation).
3. **A ≈ B at equilibrium** is a clean null for V2 vs V1 — strengthens Phase 3: if V4 lifts and V2 does not, **adaptation** is the mechanism.

**Honest write-up line:** Search provided an initial advantage during placement (+179) but did not sustain a rating differential at equilibrium, suggesting the base policy evaluation is the binding constraint.

**Pre–Phase 2 diagnostic (optional):** Sample B’s *post-convergence* replays and compare search overrides vs A’s policy — frequent overrides + identical WR ⇒ evaluation bug; rare overrides ⇒ time budget too tight.

## Logged replay sample (early / mid window)

| Baseline | Logged replays | W–L | Logged win rate |
|----------|---------------:|----:|----------------:|
| baseline_a | 9 | 4–5 | 44.4% |
| baseline_b | 10 | 5–5 | 50.0% |

Early-window sample favored B (+5.6 pp WR, +179 peak rating). Do **not** treat that as the sustained online result — equilibrium is A ≈ B at ~507.

## Replay layout

```
logs/phase1_logs/
  baseline_a/{won,lost}/<episode_id>.json
  baseline_b/{won,lost}/<episode_id>.json
```

## Analyze

```bash
python notebooks/analyze_kaggle_match_logs.py \
  --rating baseline_a=507 --rating baseline_b=507
```

(Use peak values `433` / `612` only when regenerating early-window comparison tables.)

## Artifacts

| File | Description |
|------|-------------|
| [KAGGLE_ANALYSIS.md](KAGGLE_ANALYSIS.md) | Full ladder replay EDA |
| [results/kaggle_log_analysis.json](results/kaggle_log_analysis.json) | Machine-readable stats |

## Tasks

1. ~~Submit Baseline A~~ — peak **433**, equilibrium **~507**
2. ~~Submit Baseline B~~ — peak **612**, equilibrium **~507**
3. ~~Document convergence~~ — recorded above
4. Optional: post-convergence override diagnostic; more won/lost replays

Package via workbench section 6 (`build_submission()`); set `PATHS.main_py` to the chosen baseline before building.

Offline holdout: [../offline/HOLDOUT_LOG.md](../offline/HOLDOUT_LOG.md).
