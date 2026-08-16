# Phase 3 — Offline holdout log

2×2 ablation (V1–V4) on **committed Dragapult deck**, **holdout panel v2**, **repaired `choose()`**.

**Phase 3 status:** complete — see [`../PHASE_03_COMPLETION.md`](../PHASE_03_COMPLETION.md) · [`../PHASE_03_RESULTS.json`](../PHASE_03_RESULTS.json)

Full analysis: [`HOLDOUT_ANALYSIS.md`](HOLDOUT_ANALYSIS.md) (paper Table 1 source).

## Protocol

| Field | Value |
|-------|-------|
| Total games | **640** (4 versions × 4 opponents × 40 games) |
| Deck | `data/decks/dragapult.csv` |
| Panel | **v2** (upgraded Crustle/Spidops/Starmie lists) |
| Search budget (holdout) | `PTCG_SEARCH_TIME_BUDGET=0.3` s, 8 UCB1 candidates (V2, V4); submission default 1.5 s |
| Seeds | `md5(opponent:game_idx)` — shared across variants; no `baseline_name`; no salted `hash()` |
| Validity | Holdout **fails** if `POLICY_CHOOSE_FAIL > 0` or `POLICY_CHOOSE_OK == 0` |
| CLI | `scripts/run_phase3_holdout.py` |
| Analyzer | `scripts/analyze_phase3_results.py` → `PHASE_03_RESULTS.json` |

## Ablation matrix

| Version | Search | Adaptation | Agent |
|---------|:------:|:----------:|-------|
| V1 | ✗ | ✗ | `main_baseline_a.py` |
| V2 | ✓ | ✗ | `main_baseline_b.py` |
| V3 | ✗ | ✓ | `main_baseline_v3.py` |
| V4 | ✓ | ✓ | `main_baseline_merged.py` |

## Results (canonical — repaired policy)

Source: [`results/phase3_holdout_summary_latest.json`](results/phase3_holdout_summary_latest.json)

Policy health: V1 `ok=11831 fail=0`; V3 `ok=12797 fail=0`; V2 `ok=8194 fail=0 search_ok=1752093`; V4 `ok=7407 fail=0 search_ok=2104340`.

### Per-matchup

| Opponent | V1 | V2 | V3 | V4 | V2−V1 | V3−V1 | V4−V2 | V4−V3 |
|----------|-----:|-----:|-----:|-----:|------:|------:|------:|------:|
| alakazam | 65.0% (26/40) | 5.0% (2/40) | 60.0% (24/40) | 5.0% (2/40) | −60.0 pp | −5.0 pp | 0.0 pp | −55.0 pp |
| crustle | 97.5% (39/40) | 52.5% (21/40) | 82.5% (33/40) | 47.5% (19/40) | −45.0 pp | **−15.0 pp** | −5.0 pp | −35.0 pp |
| spidops | 97.5% (39/40) | 50.0% (20/40) | 100.0% (40/40) | 37.5% (15/40) | −47.5 pp | +2.5 pp | −12.5 pp | −62.5 pp |
| starmie | 100.0% (40/40) | 37.5% (15/40) | 97.5% (39/40) | 47.5% (19/40) | **−62.5 pp** | −2.5 pp | +10.0 pp | −50.0 pp |

### Pooled (160 games each)

| Version | Record | Gate failures |
|---------|-------:|---------------|
| **V1** | **90.0%** (144/160) | none |
| V3 | 85.0% (136/160) | none |
| V2 | 36.2% (58/160) | alakazam, spidops, starmie |
| V4 | 34.4% (55/160) | alakazam, crustle, spidops, starmie |

### Component contrasts (pooled)

| Contrast | Δ |
|----------|--:|
| Search (V2 − V1) | **−53.8 pp** |
| Adaptation (V3 − V1) | **−5.0 pp** |
| Adaptation on search (V4 − V2) | −1.9 pp |
| Search on adaptation (V4 − V3) | −50.6 pp |
| Full stack (V4 − V1) | **−55.6 pp** |

## Key observations

- **V1 wins offline** — first valid measurement of `DragapultPolicy` on panel v2.
- **Search hurts** (−53.8 pp pooled) and *did run* (millions of `search_begin` rollouts). Worst vs Starmie (−62.5 pp) and Alakazam (−60.0 pp).
- **Adaptation hurts** (−5.0 pp pooled); Crustle hypothesis **fails** (−15.0 pp). Hooks no longer nerf Phantom Dive; they switch off Budew vs 344/345 and treat `{360,361,1030,1031,721,722,723}` as water.
- **Alakazam** is still the hardest cell (V1 65.0%) but is no longer a 7.5% wipe.
- **Kaggle agent:** V1 + Dragapult (`submission.tar.gz`). Phase 4 did not change this (best search cell 57.5% still −32.5 pp vs V1).

### Superseded pre-fix table (do not cite)

V1 40.0% / V2 32.5% / V3 36.2% / V4 34.4% with overlapping CIs. All four variants hit `UnboundLocalError` and played first-option. Not an ablation.

## Cross-phase (not comparable)

| Version | Phase 1 (v1, stub) | Phase 3 pre-fix (v2, stub) | Phase 3 canonical (v2, repaired) |
|---------|-------------------:|---------------------------:|---------------------------------:|
| V1 | 66.2% | 40.0% | **90.0%** |
| V2 | 63.7% | 32.5% | 36.2% |
| V4 | 41.9% | 34.4% | 34.4% |

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
