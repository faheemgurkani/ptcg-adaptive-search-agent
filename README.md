# PTCG AI Battle Challenge

AI training agent for [The Pokémon Company - PTCG AI Battle Challenge Simulation](https://kaggle.com/competitions/pokemon-tcg-ai-battle) on Kaggle.

Build a competitive agent for the Pokémon Trading Card Game simulator (cabt engine). Each turn the agent receives an observation and returns indices of legal options.

## Research direction

This project targets a **hybrid agent**: rule-based policy backbone + Search API lookahead + opponent-adaptive scoring. Full framing (agent type, domain choice, and paper angle) is documented in [`notebooks/ptcg-merged-agent-workbench.ipynb`](notebooks/ptcg-merged-agent-workbench.ipynb) under **Research framing**.

The same notebook includes a **2-week compressed experimentation plan** (Phases 1–6, ablations, search-depth sweeps, ladder validation).

Working paper title: *Opponent-Adaptive Search in Imperfect-Information Card Games*.

## Repo layout

```
.
├── main.py          # Agent entry point (required for submission)
├── data/            # Official bundle: data/pokemon-tcg-ai-battle/ (+ optional data/deck.csv override)
├── requirements.txt # Local dev dependencies
├── notebooks/       # Merged agent workbench (see notebooks/ptcg-merged-agent-workbench.ipynb)
└── docs/            # Project docs — see docs/DOCS_README.md, docs/phases/
```

Local reference notebooks and competition downloads live in `docs/resources/`. That folder is gitignored and stays on your machine only.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the competition data into `data/pokemon-tcg-ai-battle/` (card CSVs, `sample_submission/`, `ptcg_engine/`). For local runs the notebook reads the official `cg/` SDK from `sample_submission/sample_submission/cg/`. Put your chosen deck in `data/deck.csv` to override the official sample list.

## Submission

Kaggle expects a `.tar.gz` with `main.py` and `deck.csv` at the top level (plus any helper files such as `cg/`).

Use section 6 in `notebooks/ptcg-merged-agent-workbench.ipynb` (`build_submission()`) to stage `main.py`, `deck.csv`, and `cg/` into `submission.tar.gz`.

Upload `submission.tar.gz` under **My Submissions** on the competition page.

- Max size: 197.7 MiB
- Up to 5 submissions per day
- Only your 2 most recent submissions stay active

## Key links

- [Competition page](https://kaggle.com/competitions/pokemon-tcg-ai-battle)
- [Simulator API (cabt)](https://matsuoinstitute.github.io/cabt/)
- [kaggle-environments](https://github.com/Kaggle/kaggle-environments)

## Deadlines (UTC)

| Date | Milestone |
|------|-----------|
| Aug 9, 2026 | Entry and team merger deadline |
| Aug 16, 2026 | Final submission deadline |
| Aug 17–31, 2026 | Final evaluation period |
