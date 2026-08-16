# Experiment phases

Phase-wise documentation is split into **offline** (local holdout / lab) and **online** (Kaggle ladder / live).

| Phase | Goal | Offline | Online |
|-------|------|---------|--------|
| [Phase 1 — Baseline](phase_01/README.md) (**complete**) | Baseline A/B + holdout harness | [Holdout log](phase_01/offline/HOLDOUT_LOG.md) | [Kaggle log](phase_01/online/KAGGLE_LOG.md) · [Completion](phase_01/PHASE_01_COMPLETION.md) |
| [Phase 2 — Deck selection](phase_02/README.md) (**complete**) | Commit Dragapult under meta uncertainty | [Holdout log](phase_02/offline/HOLDOUT_LOG.md) | [Decision](phase_02/DECK_SELECTION_DECISION.json) · [Completion](phase_02/PHASE_02_COMPLETION.md) |
| [Phase 3 — Ablation](phase_03/README.md) (**complete**) | V1–V4 on repaired policy; V1 90.0% | [HOLDOUT log](phase_03/offline/HOLDOUT_LOG.md) | [Results JSON](phase_03/PHASE_03_RESULTS.json) · [Completion](phase_03/PHASE_03_COMPLETION.md) |
| [Phase 4 — Search depth](phase_04/README.md) (**complete**) | UCB1 candidates × time on V2; best 57.5% still ≪ V1 | [Holdout log](phase_04/offline/HOLDOUT_LOG.md) | [Results](phase_04/PHASE_04_RESULTS.json) · [Completion](phase_04/PHASE_04_COMPLETION.md) |
| [Phase 5 — Adaptation](phase_05/README.md) (**offline complete**) | V1 vs V3 impact; no extra detector | [Analysis](phase_05/offline/HOLDOUT_ANALYSIS.md) | — |
| [Phase 6 — Ladder](phase_06/README.md) (**package ready**) | V1 transfer to live ladder | — | [Status](phase_06/PHASE_06_STATUS.json) |

Master schedule: [`RESEARCH_EXPERIMENTATION_PLAN.md`](../RESEARCH_EXPERIMENTATION_PLAN.md).
