# Phase 2 — Offline holdout log

Local Dragapult vs Starmie deck evaluation against the fixed panel (Alakazam, Crustle, Spidops, Starmie).

**Phase 2 status:** complete (re-run after `choose()` fix) — see [`../README.md`](../README.md).

## Completed

- Materialized candidate decks under `data/decks/`:
  - **Dragapult** — extracted from Phase 1 ladder replay (matches `DragapultPolicy` constants)
  - **Starmie** — constructed Misty/Mega Starmie 60-list (includes 1030/1031)
- Candidate agents:
  - Dragapult → `notebooks/agents/main_baseline_a.py` (no search; `choose()` globals fixed)
  - Starmie → `notebooks/agents/main_starmie_heuristic.py` (lightweight heuristic)
- Upgraded panel decks: ladder Crustle list; constructed Spidops + Starmie lists (agents still random except Alakazam)
- Holdout CLI: `scripts/run_phase2_holdout.py` (paired `md5(opponent:game_idx)` seeds; smoke-fails if `choose()` raises)
- Meta edge analyzer: `scripts/analyze_phase2_results.py` + `scripts/meta_snapshot.py`

## Run

```bash
.venv/bin/python scripts/run_phase2_holdout.py --games 40
.venv/bin/python scripts/analyze_phase2_results.py --commit
```

## Results (canonical — repaired policy, 40 games/matchup)

Source: [`results/phase2_holdout_summary_latest.json`](results/phase2_holdout_summary_latest.json)  
Artifact stamp: `phase2_holdout_*_20260815T211810Z.csv`

Policy health (Dragapult): `choose_ok=12811`, `choose_fail=0`, `non_fallback=8012`.

| Candidate | Opponent | Win rate | Record | Gate (≥52%) |
|-----------|----------|---------:|--------|-------------|
| dragapult | alakazam | 0.500 | 20/40 | fail |
| dragapult | crustle | 0.875 | 35/40 | pass |
| dragapult | spidops | 0.950 | 38/40 | pass |
| dragapult | starmie | 1.000 | 40/40 | pass |
| starmie | alakazam | 0.100 | 4/40 | fail |
| starmie | crustle | 0.750 | 30/40 | pass |
| starmie | spidops | 0.750 | 30/40 | pass |
| starmie | starmie | 0.750 | 30/40 | pass |

**Equal-weight pool:** Dragapult **83.1%** (133/160), Starmie **58.8%** (94/160).

**Usage-weighted edge** (Alakazam / Spidops / Starmie; Crustle excluded): Dragapult **+19.9 pp**, Starmie **−13.2 pp**.

**Ladder EV (meta snapshot 2026-06-28):** Starmie 53.1% vs Dragapult 49.5% (**+3.7 pp**).

### Superseded pre-fix run (do not cite)

Before the `choose()` scoping fix, the same protocol reported Dragapult 38.8% (62/160) vs Starmie 54.4% (87/160). That was first-option fallback (`UnboundLocalError` → pick index 0), not `DragapultPolicy`.

## Holdout panel (panel v2)

| Opponent | Deck | Agent |
|----------|------|-------|
| Alakazam | Meta snapshot payload B | Rule-based (unchanged from Phase 1) |
| Crustle | Ladder-extracted Dwebble/Crustle list | Random |
| Spidops | Constructed Team Rocket Tarountula/Spidops | Random |
| Starmie | Constructed Misty/Mega Starmie (1030/1031) | Random |

## Cross-phase discontinuity

| Metric | Phase 1 A (panel v1, stub) | Phase 2 Dragapult pre-fix (v2, stub) | Phase 2 Dragapult **canonical** (v2, repaired) |
|--------|---------------------------:|-------------------------------------:|-----------------------------------------------:|
| Pooled win rate | 66.2% (106/160) | 38.8% (62/160) | **83.1%** (133/160) |

Phase 1 and the pre-fix Phase 2 run both executed first-option fallback. The 66.2% → 38.8% drop is panel hardness on a stub. The canonical 83.1% is the first valid Dragapult-policy measurement on panel v2.

## Decision

**Commit Dragapult.** See [`../DECK_SELECTION_DECISION.json`](../DECK_SELECTION_DECISION.json) and [`HOLDOUT_ANALYSIS.md`](HOLDOUT_ANALYSIS.md).

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated EDA + decision writeup |
| [results/phase2_holdout_summary_latest.json](results/phase2_holdout_summary_latest.json) | Latest summary |
| [results/](results/) | Timestamped CSV runs |
