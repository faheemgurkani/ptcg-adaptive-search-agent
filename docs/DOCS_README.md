# Docs

## cabt engine docs (local mirror)

- [`CABT_DOCS_INDEX.md`](CABT_DOCS_INDEX.md) — tracked map to offline cabt documentation under `docs/resources/cabt/` (HTML mirror, SDK snapshot, Markdown API extracts).
- Refresh + verify: `bash docs/resources/cabt/scripts/refresh_cabt_docs.sh` then `bash docs/resources/cabt/scripts/verify_cabt_runtime.sh` (uses `.venv`).

## Research plan

- [`RESEARCH_EXPERIMENTATION_PLAN.md`](RESEARCH_EXPERIMENTATION_PLAN.md) — 2-week sprint version of the full 6-phase research & experimentation plan for `ptcg-adaptive-search-agent` (phases unchanged; schedule compressed from 8 weeks to 14 days).

## Phase 1 (baseline establishment)

- [`PHASE_01_LOG.md`](PHASE_01_LOG.md) — local completion log, holdout results, Kaggle submission checklist.
- Notebook: [`notebooks/PHASE_01_BASELINE_EVAL.ipynb`](../notebooks/PHASE_01_BASELINE_EVAL.ipynb)
- Run holdout: `python notebooks/run_phase1_holdout.py --games 40`

## Local-only resources

The `docs/resources/` folder is **not tracked by git** (see `.gitignore`).

Use it for:

- Kaggle reference notebooks
- Competition datasets downloaded locally
- Notes, meta snapshots, and experiments

Keep competition-specific or large files there so they are not pushed to GitHub.

## Local extraction scripts

Notebook extraction outputs live in `data/extractions/` (gitignored). They stay on your machine only.
