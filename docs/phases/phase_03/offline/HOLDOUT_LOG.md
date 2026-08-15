# Phase 3 — Offline holdout log

2×2 ablation (V1–V4) on **committed Dragapult deck**, **holdout panel v2**.

**Phase 3 status:** complete — see [`../PHASE_03_COMPLETION.md`](../PHASE_03_COMPLETION.md).

## Protocol

- **640 games** total: 4 versions × 4 opponents × 40 games
- Deck: `data/decks/dragapult.csv`
- Panel: v2 (upgraded Crustle/Spidops/Starmie lists)
- CLI: `scripts/run_phase3_holdout.py`

## Ablation matrix

| Version | Search | Adaptation | Agent |
|---------|:------:|:----------:|-------|
| V1 | ✗ | ✗ | `main_baseline_a.py` |
| V2 | ✓ | ✗ | `main_baseline_b.py` |
| V3 | ✗ | ✓ | `main_baseline_v3.py` |
| V4 | ✓ | ✓ | `main_baseline_merged.py` |

## Results (canonical)

Source: [`results/phase3_holdout_summary_latest.json`](results/phase3_holdout_summary_latest.json)

| Version | Alakazam | Crustle | Spidops | Starmie | Pooled |
|---------|----------|---------|---------|---------|--------|
| V1 | 7.5% (3/40) | 27.5% (11/40) | 72.5% (29/40) | 52.5% (21/40) | **40.0%** |
| V2 | 5.0% (2/40) | 27.5% (11/40) | 65.0% (26/40) | 32.5% (13/40) | **32.5%** |
| V3 | 5.0% (2/40) | 20.0% (8/40) | 70.0% (28/40) | 50.0% (20/40) | **36.2%** |
| V4 | 2.5% (1/40) | 27.5% (11/40) | 67.5% (27/40) | 40.0% (16/40) | **34.4%** |

### Component contrasts (pooled)

| Contrast | Δ |
|----------|--:|
| Search (V2 − V1) | **−7.5 pp** |
| Adaptation (V3 − V1) | **−3.8 pp** |
| Adaptation on search (V4 − V2) | **+1.9 pp** |
| Search on adaptation (V4 − V3) | **−1.9 pp** |
| Full stack (V4 − V1) | **−5.6 pp** |

### Key observations

- **Search hurts pooled** (−7.5 pp vs V1); largest drop vs Starmie (−20 pp).
- **Adaptation alone hurts Crustle** (V3 − V1 = −7.5 pp on stall matchup — opposite of hypothesis).
- **V4 (full)** does not beat V1 on any pooled metric; best single matchup remains V1 vs Spidops (72.5%).
- All versions fail vs Alakazam (rule-based opponent).

## Run

```bash
.venv/bin/python scripts/run_phase3_holdout.py --games 40
.venv/bin/python scripts/analyze_phase3_results.py
```

## Artifacts

| File | Description |
|------|-------------|
| [HOLDOUT_ANALYSIS.md](HOLDOUT_ANALYSIS.md) | Generated ablation report |
| [results/phase3_holdout_summary_latest.json](results/phase3_holdout_summary_latest.json) | Latest summary |
