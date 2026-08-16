# Experiment phases

Phase-wise documentation is split into **offline** (local holdout / lab) and **online** (Kaggle ladder / live).

| Phase | Goal | Offline | Online |
|-------|------|---------|--------|
| [Phase 1 — Baseline](phase_01/README.md) (**complete**) | Baseline A/B + holdout harness | [Holdout log](phase_01/offline/HOLDOUT_LOG.md) | [Kaggle log](phase_01/online/KAGGLE_LOG.md) · [Completion](phase_01/PHASE_01_COMPLETION.md) |
| [Phase 2 — Deck selection](phase_02/README.md) (**complete**) | Commit Dragapult under meta uncertainty | [Holdout log](phase_02/offline/HOLDOUT_LOG.md) | [Decision](phase_02/DECK_SELECTION_DECISION.json) · [Completion](phase_02/PHASE_02_COMPLETION.md) |
| [Phase 3 — Ablation](phase_03/README.md) (**complete**) | V1–V4 on repaired policy; V1 90.0% | [HOLDOUT log](phase_03/offline/HOLDOUT_LOG.md) | [Results JSON](phase_03/PHASE_03_RESULTS.json) · [Completion](phase_03/PHASE_03_COMPLETION.md) |
| [Phase 4 — Search depth](phase_04/README.md) (**in progress**) | UCB1 candidates × time budget on V2 | [Holdout log](phase_04/offline/HOLDOUT_LOG.md) | [Completion](phase_04/PHASE_04_COMPLETION.md) |
| Phase 5 | Opponent adaptation | *(pending)* | *(pending)* |
| Phase 6 | Live ladder validation | *(pending)* | *(pending)* |

Master schedule: [`RESEARCH_EXPERIMENTATION_PLAN.md`](../RESEARCH_EXPERIMENTATION_PLAN.md).
