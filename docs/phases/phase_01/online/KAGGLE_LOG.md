# Phase 1 — Online Kaggle log

Live ladder submissions and downloaded replay analysis.

## Submissions

| Baseline | Agent | Ladder rating | Status |
|----------|-------|--------------:|--------|
| baseline_a | Dragapult, no search | **433** | Submitted |
| baseline_b | Dragapult + UCB1 search | **612** | Submitted |

Ratings come from the Kaggle UI — they are **not** embedded in replay JSON files.

## Logged replay sample

| Baseline | Logged replays | W–L | Logged win rate |
|----------|---------------:|----:|----------------:|
| baseline_a | 9 | 4–5 | 44.4% |
| baseline_b | 10 | 5–5 | 50.0% |

**Interpretation:** Baseline B leads by **+179 rating** and **+5.6 pp** on downloaded replays. That aligns with search helping on the ladder, but replays are a small subset of all games behind each rating.

## Replay layout

```
logs/phase1_logs/
  baseline_a/{won,lost}/<episode_id>.json
  baseline_b/{won,lost}/<episode_id>.json
```

## Analyze

```bash
python notebooks/analyze_kaggle_match_logs.py \
  --rating baseline_a=433 --rating baseline_b=612
```

## Artifacts

| File | Description |
|------|-------------|
| [KAGGLE_ANALYSIS.md](KAGGLE_ANALYSIS.md) | Full ladder replay EDA |
| [results/kaggle_log_analysis.json](results/kaggle_log_analysis.json) | Machine-readable stats |

## Tasks

1. ~~Submit Baseline A~~ — rating **433**
2. ~~Submit Baseline B~~ — rating **612**
3. Refresh ratings here when they move
4. Optional: add more won/lost replays and re-run the analyzer

Package via workbench section 6 (`build_submission()`); set `PATHS.main_py` to the chosen baseline before building.

Offline holdout: [../offline/HOLDOUT_LOG.md](../offline/HOLDOUT_LOG.md).
