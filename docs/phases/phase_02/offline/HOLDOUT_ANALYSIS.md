# Phase 2 — Deck selection analysis

## Per-matchup win rates (local holdout)

| Candidate | Alakazam | Crustle | Spidops | Starmie | Equal-weight pool |
|-----------|----------|---------|---------|---------|-------------------|
| dragapult | 7.5% (3/40) | 25.0% (10/40) | 45.0% (18/40) | 45.0% (18/40) | 30.6% |
| starmie | 5.0% (2/40) | 72.5% (29/40) | 85.0% (34/40) | 67.5% (27/40) | 57.5% |

## Meta-weighted edge (usage share × matchup)

Weights from meta snapshot field chart. Panel rows without a meta mapping (currently **crustle**) are skipped for the weighted edge — they still appear in the equal-weight pool above.

| Candidate | Weighted score | Field score (usage-weighted) | Edge vs field | Coverage |
|-----------|----------------|------------------------------|---------------|----------|
| dragapult | 24.1% | 52.0% | -27.9% | 34.0% |
| starmie | 33.3% | 52.0% | -18.7% | 34.0% |

### Matchup-level edges (winner candidate detail)

- vs **alakazam** (alakazam_dunsparce): our 7.5% vs field score 51.3% (usage 19.0%) → matchup edge -43.8%
- vs **spidops** (team_rocket_spidops): our 45.0% vs field score 64.1% (usage 1.2%) → matchup edge -19.1%
- vs **starmie** (starmie): our 45.0% vs field score 51.9% (usage 13.9%) → matchup edge -6.9%

## Ladder EV reference (meta snapshot, not local holdout)

- **dragapult**: usage 7.3%, field score 49.1%, matchup-weighted EV 49.5%
- **starmie**: usage 13.9%, field score 51.9%, matchup-weighted EV 53.1%

## Decision

**Committed deck: `dragapult`**

- Local holdout meta-weighted leader: starmie (edge -0.187, weighted score 0.333).
- Ladder EV gap (Starmie − Dragapult) = +3.7% (53.1% vs 49.5%).
- Ladder EV gap < 5pp and local comparison is agent-asymmetric (DragapultPolicy vs thin Starmie heuristic) → commit Dragapult so Phase 3–5 ablations remain on a single policy stack. Starmie's local win is noted as a sensitivity check, not an equal-pilot deck verdict.
- Meta snapshot (2026-06-28) ladder EV: Starmie usage=13.9% score=51.9% EV=53.1%; Dragapult usage=7.3% score=49.1% EV=49.5%.

## Caveats

- Dragapult uses Baseline A (`DragapultPolicy`, no search) — matches Phase 3 V1.
- Starmie uses a lightweight heuristic agent, not a full public rule-based pilot; local Starmie win rates are a lower bound on what a tuned Starmie policy might achieve.
- Crustle/Spidops opponents remain random-policy; Crustle/Spidops/Starmie decks were upgraded for Phase 2 (ladder Crustle list; constructed Spidops/Starmie lists).
- Meta weights: Alakazam→alakazam_dunsparce, Spidops→team_rocket_spidops, Starmie→starmie; Crustle excluded from usage-weighted edge.
