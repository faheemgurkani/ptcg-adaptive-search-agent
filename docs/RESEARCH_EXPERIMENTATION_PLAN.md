# Research & Experimentation Plan for `ptcg-adaptive-search-agent`

Compressed from the original 8-week plan into a **14-day sprint**. Phase goals, tasks, and paper mapping are **unchanged** — only the schedule is tighter.

Related: [`notebooks/ptcg-merged-agent-workbench.ipynb`](../notebooks/ptcg-merged-agent-workbench.ipynb) (executable workbench).

---

## The Core Research Question

> *Does opponent-adaptive heuristic search outperform static rule-based policy in an imperfect-information card game, and by how much does each component contribute?*

This gives you one clean thesis for both the paper and the Kaggle writeup.

---

## Two-Week Calendar (14 Days)

| Days | Original window | Phase |
|------|-----------------|-------|
| 1–2 | Week 1–2 | Phase 1 — Baseline establishment |
| 3–4 | Week 2–3 | Phase 2 — Deck selection & meta analysis |
| 5–9 | Week 3–5 | Phase 3 — Ablation study |
| 10–11 | Week 4–5 | Phase 4 — Search depth analysis |
| 11–12 | Week 5–6 | Phase 5 — Opponent adaptation analysis |
| 13–14 | Week 6–7 | Phase 6 — Live ladder validation |

Days 11–12 overlap Phases 4 and 5 on purpose — run search sweeps in the morning, adaptation analysis in the afternoon.

---

## Phase 1 — Baseline Establishment (Days 1–2)

**Status: COMPLETE** (Merged ladder ratings pending) — see [`phases/phase_01/PHASE_01_COMPLETION.md`](phases/phase_01/PHASE_01_COMPLETION.md).

**Goal:** Get a working submission and a reproducible evaluation harness.

**Tasks:**

- [x] Submit the Dragapult-only policy (no search, no opponent detection) as **Baseline A** — peak **433** → ~**507**
- [x] Submit Dragapult + UCB1 Search as **Baseline B** — peak **612** → ~**507**
- [x] Submit Dragapult + UCB1 + adaptation as **Merged (C / V4)** — ladder ratings TBD
- [x] Record A/B ladder ratings — [`phases/phase_01/online/KAGGLE_LOG.md`](phases/phase_01/online/KAGGLE_LOG.md)
- [x] Implement `run_holdout_suite()` — A/B/Merged vs Alakazam / Crustle / Spidops / Starmie; [`phases/phase_01/offline/`](phases/phase_01/offline/)

**Why it matters for paper:** Clean ablation starting points. A = no search. B = search, no adaptation. C = search + adaptation (early V4). Offline C currently **−21.9 pp** vs B on this panel.

---

## Phase 2 — Deck Selection & Meta Analysis (Days 3–4)

**Status: COMPLETE** — committed **Dragapult** (`data/deck.csv`). See [`phases/phase_02/PHASE_02_COMPLETION.md`](phases/phase_02/PHASE_02_COMPLETION.md).

**Goal:** Pick and commit to a deck with a principled justification.

**Tasks:**

- [x] Run holdout suite with both Dragapult and Starmie decks against the four key archetypes
- [x] Record win rates per matchup, not just overall
- [x] Apply the meta snapshot logic: usage share vs. actual score rate — pick with field-composition edge (ladder EV primary under agent asymmetry)
- [x] Document deck selection decision — Section 2 / [`phases/phase_02/`](phases/phase_02/)

**Decision:** Commit **Dragapult** before Phase 3. Canonical local holdout favors Dragapult (**83.1%** vs Starmie **58.8%**). Ladder EV gap vs Starmie +3.7 pp (<5 pp).

**Holdout panel v2:** Before Phase 2, Crustle/Spidops/Starmie opponent decks were upgraded (ladder Crustle; constructed Spidops/Starmie). Phase 1 used **panel v1** and a broken `choose()` (first-option stub). **Do not compare Phase 1 stub rates to repaired Phase 2/3 rates.**

**Phase 2 canonical offline (panel v2, repaired policy, 40 games/matchup):**

| Candidate | Alakazam | Crustle | Spidops | Starmie | Pool |
|-----------|----------|---------|---------|---------|------|
| Dragapult | 50.0% | 87.5% | 95.0% | 100.0% | **83.1%** |
| Starmie | 10.0% | 75.0% | 75.0% | 75.0% | 58.8% |

Meta-weighted edge: Dragapult **+19.9 pp**, Starmie **−13.2 pp**. Ladder EV: Starmie 53.1% vs Dragapult 49.5%. Pre-fix 38.8%/54.4% is superseded (first-option stub).

---

## Phase 3 — Ablation Study (Days 5–9)

**Status: COMPLETE** — see [`phases/phase_03/PHASE_03_COMPLETION.md`](phases/phase_03/PHASE_03_COMPLETION.md).

**Goal:** Isolate the contribution of each component. This is the heart of the paper.

| Agent Version | Search | Opponent Detection | Offline pool (panel v2, repaired) |
|---|---|---|---|
| V1 | ✗ | ✗ | **90.0%** (144/160) |
| V2 | ✓ UCB1 | ✗ | 36.2% (−53.8 pp vs V1) |
| V3 | ✗ | ✓ Adaptive weights | 85.0% (−5.0 pp vs V1) |
| V4 | ✓ UCB1 | ✓ Adaptive weights | 34.4% (−55.6 pp vs V1) |

**Key finding:** After the `choose()` scoping fix, V1 is a real policy (90.0%). Search *runs* and **hurts** (−53.8 pp). Adaptation **hurts** (−5.0 pp; Crustle −15.0 pp). Pre-fix 40.0/32.5/36.2/34.4% is first-option noise. Kaggle submission stays V1 + Dragapult.

**Phase 4 follow-up:** Extra search compute does not recover V1 (best searched cell 57.5% at 4 candidates / 1.5 s, −32.5 pp). See Phase 4 below.

**Phase 5 note:** Phase 3 already compared V1 vs V3 on Crustle (−15.0 pp); Phase 5 adds detector logging and false-positive analysis.

---

## Phase 4 — Search Depth Analysis (Days 10–11)

**Goal:** Answer how much search depth actually matters given the time budget.

**Status:** complete (repaired V2, panel v2, Dragapult). 7 cells × 160 games.

**Results:** Best cell 4 candidates / 1.5 s at **57.5%** (−32.5 pp vs V1 90.0%). Time knee 0.5 s (8-candidate curve is flat then drops at 2.0 s). Candidate knee 4 (wider UCB1 sets hurt). No searched cell approaches V1.

**Protocol:**

- Agent: **V2 only** (search on, adaptation off) so the curve isolates compute, not opponent hooks.
- Candidates `{4, 8, 12, 16}` and time budgets `{0.5, 1.0, 1.5, 2.0}` s per MAIN decision (`PTCG_SEARCH_MAX_CANDIDATES`, `PTCG_SEARCH_TIME_BUDGET`).
- Default: two 1-D sweeps (8 candidates × all times; 1.5 s × remaining candidate counts) = 7 cells × 160 games. `--grid` runs the full 4×4.
- Plot win rate vs compute; find the knee (smallest budget within 2 pp of the best point on that curve).
- Phase 3 V1 90.0% and V2 36.2% (0.3 s / 8 candidates) are labeled references only.

**Why it matters for paper:** This is Figure 2. It directly addresses the practical compute–performance tradeoff in real-time game AI.

CLI: `scripts/run_phase4_holdout.py --games 40` · `scripts/analyze_phase4_results.py`

---

## Phase 5 — Opponent Adaptation Analysis (Days 11–12)

**Goal:** Show that adaptive weights matter and quantify how much.

**Tasks:**

- Against Crustle specifically: compare V1 vs V3 (Dragapult policy vs. Dragapult + Crustle-aware weights)
- Log which archetype was detected and when during games
- Track false positive rate — does the detector misidentify archetypes early game when the bench is empty?
- Consider adding one more archetype detector beyond what the Expectimax agent has (e.g., Spidops or Festival detection)

**Why it matters for paper:** Opponent modeling in hidden-information games is a known hard problem. Even a simple detector with real impact is a publishable contribution if properly measured.

---

## Phase 6 — Live Ladder Validation (Days 13–14)

**Goal:** Confirm offline results transfer to the live ladder.

**Tasks:**

- Submit **V1 + Dragapult** (search/adaptation did not help offline, including Phase 4 compute sweeps) and record ladder rating over time
- Compare per-archetype matchup rates on the ladder vs. your holdout panel
- Measure the gap — if holdout says 70% vs Crustle but ladder shows 60%, that's a calibration finding worth reporting
- Apply the winner's curse check from the meta snapshot: if your holdout score drops significantly on a fresh panel, prefer the more stable configuration

---

## Paper Structure (Target: CoG 2027 or AAAI Workshop)

| Section | Content | Source |
|---|---|---|
| Introduction | Imperfect-info card games as AI testbeds | Literature |
| Background | PTCG mechanics, PIMC, UCB1, opponent modeling | Literature |
| System Design | Dragapult policy + Search + Adaptation | Phase 1–2 |
| Deck Selection | Meta-informed deck choice methodology | Phase 2 |
| Experiments | Ablation table, search depth curve (done), adaptation analysis | Phase 3–5 |
| Live Evaluation | Ladder validation, holdout-to-live transfer gap | Phase 6 |
| Conclusion | What worked, what didn't, future work | All |

---

## One Rule to Follow Throughout

**Document every decision as you make it, not at the end.** Every time you change a weight, add a detector, or switch a parameter — write one paragraph explaining why. That becomes your Kaggle writeup organically, and it becomes your paper's experimental section with almost no additional work.
