# Docs

## Scripts

- [`../scripts/README.md`](../scripts/README.md) — CLI modules (`env_paths`, holdout, analyzers, agent build).

## Data and logs

- [`DATA_AND_LOGS.md`](DATA_AND_LOGS.md) — inventory of competition data, decks, holdout panel, offline results, and Kaggle ladder replays (origin, placement, use, preprocessing).

## Research plan

- [`RESEARCH_EXPERIMENTATION_PLAN.md`](RESEARCH_EXPERIMENTATION_PLAN.md) — 2-week sprint (Phases 1–6).

## Experiment phases (offline + online)

- [`phases/README.md`](phases/README.md) — phase index
- **Phase 1 — Baseline (complete):** [`phases/phase_01/README.md`](phases/phase_01/README.md) · [`PHASE_01_COMPLETION.md`](phases/phase_01/PHASE_01_COMPLETION.md)
  - Offline holdout: [`phases/phase_01/offline/HOLDOUT_LOG.md`](phases/phase_01/offline/HOLDOUT_LOG.md)
  - Online Kaggle: [`phases/phase_01/online/KAGGLE_LOG.md`](phases/phase_01/online/KAGGLE_LOG.md)
- **Phase 2 — Deck selection (complete):** [`phases/phase_02/README.md`](phases/phase_02/README.md) · [`PHASE_02_COMPLETION.md`](phases/phase_02/PHASE_02_COMPLETION.md)
  - Decision: **Dragapult** — [`DECK_SELECTION_DECISION.json`](phases/phase_02/DECK_SELECTION_DECISION.json)
  - **Holdout panel v2** (upgraded opponent decks); Phase 1 used **panel v1** — win rates are not cross-comparable
- **Phase 3 — Ablation (complete):** [`phases/phase_03/README.md`](phases/phase_03/README.md) · [`PHASE_03_COMPLETION.md`](phases/phase_03/PHASE_03_COMPLETION.md) · [`PHASE_03_RESULTS.json`](phases/phase_03/PHASE_03_RESULTS.json)
  - V1–V4 on panel v2 (repaired `choose()`); **V1 strongest** (90.0% pooled); search −53.8 pp, adaptation −5.0 pp

Legacy redirect: [`PHASE_01_LOG.md`](PHASE_01_LOG.md).

## cabt engine docs (local mirror)

- [`CABT_DOCS_INDEX.md`](CABT_DOCS_INDEX.md) — map to `docs/resources/cabt/`
- Refresh + verify: `bash docs/resources/cabt/scripts/refresh_cabt_docs.sh` then `bash docs/resources/cabt/scripts/verify_cabt_runtime.sh`

## Local-only resources

The `docs/resources/` folder is **not tracked by git** (see `.gitignore`). Use it for reference notebooks, datasets, and cabt mirrors.

Notebook extraction outputs live in `data/extractions/` (gitignored).
