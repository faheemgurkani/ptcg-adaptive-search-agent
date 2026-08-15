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

**Decision:** Commit **Dragapult** before Phase 3. Ladder EV gap vs Starmie +3.7pp (<5pp); local Starmie lead is agent-asymmetric.

**Holdout panel v2:** Before Phase 2, Crustle/Spidops/Starmie opponent decks were upgraded (ladder Crustle; constructed Spidops/Starmie). Phase 1 canonical numbers used **panel v1** (placeholder decks). **Do not compare Phase 1 and Phase 2 win rates directly** (e.g. Baseline A 66.2% vs Phase 2 Dragapult 38.8% reflects panel hardness, not agent regression).

**Phase 2 canonical offline (panel v2, 40 games/matchup):**

| Candidate | Alakazam | Crustle | Spidops | Starmie | Pool |
|-----------|----------|---------|---------|---------|------|
| Dragapult | 2.5% | 25.0% | 77.5% | 50.0% | 38.8% |
| Starmie | 2.5% | 67.5% | 82.5% | 65.0% | 54.4% |

Meta-weighted edge: Dragapult −27.5pp, Starmie −21.2pp. Ladder EV: Starmie 53.1% vs Dragapult 49.5%.

---

## Phase 3 — Ablation Study (Days 5–9)

**Goal:** Isolate the contribution of each component. This is the heart of the paper.

Run four agent configurations against your fixed holdout panel:

| Agent Version | Search | Opponent Detection | Expected Role |
|---|---|---|---|
| V1 | ✗ | ✗ | Pure Dragapult baseline |
| V2 | ✓ UCB1 | ✗ | Search contribution |
| V3 | ✗ | ✓ Adaptive weights | Adaptation contribution |
| V4 | ✓ UCB1 | ✓ Adaptive weights | Full system |

Measure per matchup win rate, not just overall. You want to show that opponent detection helps specifically against Crustle/stall matchups, and search helps in tactical decision points.

**This is your Table 1 in the paper.**

---

## Phase 4 — Search Depth Analysis (Days 10–11)

**Goal:** Answer how much search depth actually matters given the time budget.

**Tasks:**

- Vary UCB1 candidate count: 4, 8, 12, 16 candidates
- Vary time budget: 0.5s, 1.0s, 1.5s, 2.0s per decision
- Plot win rate vs. compute budget curve
- Find the knee — where does additional search stop helping?

**Why it matters for paper:** This is your Figure 2. It directly addresses the practical question of compute-performance tradeoff in real-time game AI, which is a standard analysis in MCTS literature.

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

- Submit V4 (full system) and record ladder rating over time
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
| Experiments | Ablation table, search depth curve, adaptation analysis | Phase 3–5 |
| Live Evaluation | Ladder validation, holdout-to-live transfer gap | Phase 6 |
| Conclusion | What worked, what didn't, future work | All |

---

## One Rule to Follow Throughout

**Document every decision as you make it, not at the end.** Every time you change a weight, add a detector, or switch a parameter — write one paragraph explaining why. That becomes your Kaggle writeup organically, and it becomes your paper's experimental section with almost no additional work.
