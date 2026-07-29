# Phase 1 — Online Kaggle log

Live ladder submissions and downloaded replay analysis.

**Phase 1 status:** A/B complete online; **Merged submitted — ratings/replays pending** — see [`../PHASE_01_COMPLETION.md`](../PHASE_01_COMPLETION.md).

## Submissions and ratings

| Baseline | Agent | Early peak | Equilibrium | Status |
|----------|-------|----------:|------------:|--------|
| baseline_a | Dragapult, no search | **433** | **~507** | Submitted |
| baseline_b | Dragapult + UCB1 search | **612** | **~507** | Submitted |
| baseline_merged (C) | Dragapult + UCB1 + adaptation | *TBD* | *TBD* | **Submitted** (logs forthcoming) |

Ratings come from the Kaggle UI — they are **not** embedded in replay JSON files.

### Ladder convergence (A/B — documented finding)

Both A and B **converged to ~507** after the initial placement transient.

**What this means:** Matchmaking pairs agents near their current rating. B’s early +179 lead was partly cold-start / punching-down during placement and partly a narrow search edge that did not survive once both faced the same field at the same tier.

**Implications:**
1. The **floor (~507)** is the signal, not the early gap — Dragapult base policy evaluation is the binding constraint; search alone cannot climb past it.
2. Offline search null (−2.5 pp pooled; B worse vs Alakazam) is **corroborated** online — UCB1 as configured is not a reliable win-rate lift (likely optimizing a weak evaluation).
3. **A ≈ B at equilibrium** is a clean null for V2 vs V1 — Phase 3 / Merged tests whether adaptation breaks that ceiling (offline Merged currently **worse** than B; ladder will confirm or contradict).

**Honest write-up line:** Search provided an initial advantage during placement (+179) but did not sustain a rating differential at equilibrium, suggesting the base policy evaluation is the binding constraint.

### Merged (Baseline C) — pending online metrics

Offline holdout for Merged is recorded in [`../offline/HOLDOUT_LOG.md`](../offline/HOLDOUT_LOG.md) (pooled **41.9%**, −21.9 pp vs B).

When available, add here:
- Peak / equilibrium ladder rating
- Replay JSONs under `logs/phase1_logs/baseline_merged/{won,lost}/`
- Re-run: `python scripts/analyze_kaggle_match_logs.py --rating baseline_merged=<rating>`

## Logged replay sample (early / mid window) — A/B only so far

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

## Analyze

```bash
python scripts/analyze_kaggle_match_logs.py \
  --rating baseline_a=507 --rating baseline_b=507
# later: --rating baseline_merged=<rating>
```

## Artifacts

| File | Description |
|------|-------------|
| [KAGGLE_ANALYSIS.md](KAGGLE_ANALYSIS.md) | Full ladder replay EDA (A/B) |
| [results/kaggle_log_analysis.json](results/kaggle_log_analysis.json) | Machine-readable stats |

## Tasks

1. ~~Submit Baseline A~~ — peak **433**, equilibrium **~507**
2. ~~Submit Baseline B~~ — peak **612**, equilibrium **~507**
3. ~~Document A/B convergence~~ — recorded above
4. ~~Submit Merged (C)~~ — awaiting ratings + replay download
5. Optional: post-convergence override diagnostic; more won/lost replays

Offline holdout: [../offline/HOLDOUT_LOG.md](../offline/HOLDOUT_LOG.md).
