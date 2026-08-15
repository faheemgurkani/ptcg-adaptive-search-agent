# Phase 3 — Offline holdout log

2×2 ablation (V1–V4) on **committed Dragapult deck**, **holdout panel v2**.

**Phase 3 status:** complete — see [`../PHASE_03_COMPLETION.md`](../PHASE_03_COMPLETION.md) · [`../PHASE_03_RESULTS.json`](../PHASE_03_RESULTS.json)

Full analysis: [`HOLDOUT_ANALYSIS.md`](HOLDOUT_ANALYSIS.md) (paper Table 1 source).

## Protocol

| Field | Value |
|-------|-------|
| Total games | **640** (4 versions × 4 opponents × 40 games) |
| Deck | `data/decks/dragapult.csv` |
| Panel | **v2** (upgraded Crustle/Spidops/Starmie lists) |
| Search budget | 1.5 s, 8 UCB1 candidates (V2, V4) |
| CLI | `scripts/run_phase3_holdout.py` |
| Analyzer | `scripts/analyze_phase3_results.py` → `PHASE_03_RESULTS.json` |

## Ablation matrix

| Version | Search | Adaptation | Agent |
|---------|:------:|:----------:|-------|
| V1 | ✗ | ✗ | `main_baseline_a.py` |
| V2 | ✓ | ✗ | `main_baseline_b.py` |
| V3 | ✗ | ✓ | `main_baseline_v3.py` |
| V4 | ✓ | ✓ | `main_baseline_merged.py` |

## Results (canonical)

Source: [`results/phase3_holdout_summary_latest.json`](results/phase3_holdout_summary_latest.json)

### Per-matchup

| Opponent | V1 | V2 | V3 | V4 | V2−V1 | V3−V1 | V4−V2 | V4−V3 |
|----------|-----:|-----:|-----:|-----:|------:|------:|------:|------:|
| alakazam | 7.5% (3/40) | 5.0% (2/40) | 5.0% (2/40) | 2.5% (1/40) | −2.5 pp | −2.5 pp | −2.5 pp | −2.5 pp |
| crustle | 27.5% (11/40) | 27.5% (11/40) | 20.0% (8/40) | 27.5% (11/40) | 0.0 pp | **−7.5 pp** | 0.0 pp | +7.5 pp |
| spidops | 72.5% (29/40) | 65.0% (26/40) | 70.0% (28/40) | 67.5% (27/40) | −7.5 pp | −2.5 pp | +2.5 pp | −2.5 pp |
| starmie | 52.5% (21/40) | 32.5% (13/40) | 50.0% (20/40) | 40.0% (16/40) | **−20.0 pp** | −2.5 pp | +7.5 pp | −10.0 pp |

### Pooled (160 games each)

| Version | Record | Gate failures |
|---------|-------:|---------------|
| **V1** | **40.0%** (64/160) | alakazam, crustle |
| V2 | 32.5% (52/160) | alakazam, crustle, starmie |
| V3 | 36.2% (58/160) | alakazam, crustle, starmie |
| V4 | 34.4% (55/160) | alakazam, crustle, starmie |

### Component contrasts (pooled)

| Contrast | Δ |
|----------|--:|
| Search (V2 − V1) | **−7.5 pp** |
| Adaptation (V3 − V1) | **−3.8 pp** |
| Adaptation on search (V4 − V2) | +1.9 pp |
| Search on adaptation (V4 − V3) | −1.9 pp |
| Full stack (V4 − V1) | **−5.6 pp** |

## Key observations

- **V1 wins offline** — no ablation variant beats pure policy on pooled win rate.
- **Search hurts** (−7.5 pp pooled); worst vs Starmie (−20 pp).
- **Adaptation hurts** (−3.8 pp pooled); Crustle hypothesis **fails** (−7.5 pp).
- **All versions fail vs Alakazam** (≤7.5%).
- **Kaggle agent unchanged:** Phase 2 submission = V1 + Dragapult.

## Cross-phase (panel v1 → v2, not comparable)

| Version | Phase 1 (v1) | Phase 3 (v2) |
|---------|-------------:|-------------:|
| V1 | 66.2% | 40.0% |
| V2 | 63.7% | 32.5% |
| V4 | 41.9% | 34.4% |

## Run

```bash
.venv/bin/python scripts/run_phase3_holdout.py --games 40
.venv/bin/python scripts/analyze_phase3_results.py
python docs/research_paper_writeup/generate_phase3_figures.py
```

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Full ablation report (Table 1) |
| [../PHASE_03_RESULTS.json](../PHASE_03_RESULTS.json) | Machine-readable findings |
| [results/phase3_holdout_summary_latest.json](results/phase3_holdout_summary_latest.json) | Latest summary |
| [results/](results/) | Timestamped CSV runs |
