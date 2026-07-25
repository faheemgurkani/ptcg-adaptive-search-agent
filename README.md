# PTCG AI Battle Challenge

AI training agent for [The Pokémon Company - PTCG AI Battle Challenge Simulation](https://kaggle.com/competitions/pokemon-tcg-ai-battle) on Kaggle.

Build a competitive agent for the Pokémon Trading Card Game simulator (cabt engine). Each turn the agent receives an observation and returns indices of legal options.

## Research direction

This project targets a **hybrid agent**: rule-based policy backbone + Search API lookahead + opponent-adaptive scoring. Full framing (agent type, domain choice, and paper angle) is documented in [`notebooks/ptcg-merged-agent-workbench.ipynb`](notebooks/ptcg-merged-agent-workbench.ipynb) under **Research framing**.

Working paper title: *Opponent-Adaptive Search in Imperfect-Information Card Games*.

## Repo layout

```
.
├── main.py          # Agent entry point (required for submission)
├── data/            # Competition data (deck.csv, cg/, etc.)
├── requirements.txt # Local dev dependencies
├── notebooks/       # Merged agent workbench (see notebooks/ptcg-merged-agent-workbench.ipynb)
└── docs/            # Project docs (see docs/README.md)
```

Local reference notebooks and competition downloads live in `docs/resources/`. That folder is gitignored and stays on your machine only.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add competition files under `data/` (for example `data/deck.csv` and the `cg/` library from Kaggle). Submissions bundle `main.py`, `deck.csv`, and the `cg/` package at the top level.

## Submission

Kaggle expects a `.tar.gz` with `main.py` and `deck.csv` at the top level (plus any helper files such as `cg/`).

```bash
tar -czvf submission.tar.gz main.py data/deck.csv data/cg/
# Rename paths in the archive so deck.csv and cg/ sit at the top level before upload.
```

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
