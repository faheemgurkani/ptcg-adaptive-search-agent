# Scripts

CLI and shared Python modules for the PTCG adaptive-search agent project.

| Script | Role |
|--------|------|
| `env_paths.py` | Local vs Kaggle path resolution |
| `build_merged_agent.py` | Build Baseline A/B + merged agent from reference notebooks |
| `extract_holdout_panel.py` | Materialize holdout opponent decks/agents under `notebooks/holdout/` |
| `holdout_runner.py` | `run_holdout_suite()` via `kaggle_environments` / cabt |
| `run_phase1_holdout.py` | Phase 1 holdout CLI |
| `run_phase2_holdout.py` | Phase 2 Dragapult vs Starmie holdout CLI |
| `meta_snapshot.py` | Field chart + usage-weighted edge helpers |
| `analyze_phase1_results.py` | Offline holdout EDA → `docs/phases/phase_01/offline/` |
| `analyze_phase2_results.py` | Deck selection EDA + commitment → `docs/phases/phase_02/` |
| `analyze_kaggle_match_logs.py` | Ladder replay EDA → `docs/phases/phase_01/online/` |

## Examples

```bash
# from repo root
python scripts/build_merged_agent.py --variant all
python scripts/extract_holdout_panel.py
python scripts/run_phase1_holdout.py --games 40
python scripts/analyze_phase1_results.py
python scripts/run_phase2_holdout.py --games 40
python scripts/analyze_phase2_results.py --commit
python scripts/analyze_kaggle_match_logs.py --rating baseline_a=507 --rating baseline_b=507
```

Notebooks under `notebooks/` add `scripts/` to `sys.path` and call these CLIs via subprocess.
Agent sources stay in `notebooks/agents/` and `notebooks/holdout/panel/`.
