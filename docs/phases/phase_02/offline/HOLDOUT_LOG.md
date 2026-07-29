# Phase 2 — Offline holdout log

Local Dragapult vs Starmie deck evaluation against the fixed panel (Alakazam, Crustle, Spidops, Starmie).

**Phase 2 status:** complete — see [`../README.md`](../README.md).

## Completed

- Materialized candidate decks under `data/decks/`:
  - **Dragapult** — extracted from Phase 1 ladder replay (matches `DragapultPolicy` constants)
  - **Starmie** — constructed Misty/Mega Starmie 60-list
- Candidate agents:
  - Dragapult → `notebooks/agents/main_baseline_a.py` (no search)
  - Starmie → `notebooks/agents/main_starmie_heuristic.py` (lightweight heuristic)
- Upgraded panel decks: ladder Crustle list; constructed Spidops + Starmie lists (agents still random except Alakazam)
- Holdout CLI: `scripts/run_phase2_holdout.py`
- Meta edge analyzer: `scripts/analyze_phase2_results.py` + `scripts/meta_snapshot.py`

## Run

```bash
.venv/bin/python scripts/run_phase2_holdout.py --games 40
.venv/bin/python scripts/analyze_phase2_results.py --commit
```

## Results (canonical — 40 games/matchup)

Source: [`results/phase2_holdout_summary_latest.json`](results/phase2_holdout_summary_latest.json)

| Candidate | Opponent | Win rate | Record | Gate (≥52%) |
|-----------|----------|---------:|--------|-------------|
| dragapult | alakazam | 0.075 | 3/40 | fail |
| dragapult | crustle | 0.250 | 10/40 | fail |
| dragapult | spidops | 0.450 | 18/40 | fail |
| dragapult | starmie | 0.450 | 18/40 | fail |
| starmie | alakazam | 0.050 | 2/40 | fail |
| starmie | crustle | 0.725 | 29/40 | pass |
| starmie | spidops | 0.850 | 34/40 | pass |
| starmie | starmie | 0.675 | 27/40 | pass |

**Equal-weight pool:** Dragapult 30.6% (49/160), Starmie 57.5% (92/160).

**Usage-weighted edge** (Alakazam / Spidops / Starmie; Crustle excluded): Dragapult −27.9pp, Starmie −18.7pp (both negative vs field score rates — Alakazam weight dominates).

**Ladder EV (meta snapshot 2026-06-28):** Starmie 53.1% vs Dragapult 49.5% (**+3.7pp**).

## Decision

**Commit Dragapult.** See [`../DECK_SELECTION_DECISION.json`](../DECK_SELECTION_DECISION.json) and [`HOLDOUT_ANALYSIS.md`](HOLDOUT_ANALYSIS.md).

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated EDA + decision writeup |
| [results/phase2_holdout_summary_latest.json](results/phase2_holdout_summary_latest.json) | Latest summary |
| [results/](results/) | Timestamped CSV runs |
