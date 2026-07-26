# Docs

## Research plan

- [`RESEARCH_EXPERIMENTATION_PLAN.md`](RESEARCH_EXPERIMENTATION_PLAN.md) — 2-week sprint (Phases 1–6).

## Experiment phases (offline + online)

- [`phases/README.md`](phases/README.md) — phase index
- **Phase 1 — Baseline:** [`phases/phase_01/README.md`](phases/phase_01/README.md)
  - Offline holdout: [`phases/phase_01/offline/HOLDOUT_LOG.md`](phases/phase_01/offline/HOLDOUT_LOG.md)
  - Online Kaggle: [`phases/phase_01/online/KAGGLE_LOG.md`](phases/phase_01/online/KAGGLE_LOG.md)

Legacy redirect: [`PHASE_01_LOG.md`](PHASE_01_LOG.md).

## cabt engine docs (local mirror)

- [`CABT_DOCS_INDEX.md`](CABT_DOCS_INDEX.md) — map to `docs/resources/cabt/`
- Refresh + verify: `bash docs/resources/cabt/scripts/refresh_cabt_docs.sh` then `bash docs/resources/cabt/scripts/verify_cabt_runtime.sh`

## Local-only resources

The `docs/resources/` folder is **not tracked by git** (see `.gitignore`). Use it for reference notebooks, datasets, and cabt mirrors.

Notebook extraction outputs live in `data/extractions/` (gitignored).
