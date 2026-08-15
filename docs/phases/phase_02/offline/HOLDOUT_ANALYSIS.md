# Phase 2 — Deck selection analysis

## Per-matchup win rates (local holdout)

| Candidate | Alakazam | Crustle | Spidops | Starmie | Equal-weight pool |
|-----------|----------|---------|---------|---------|-------------------|
| dragapult | 50.0% (20/40) | 87.5% (35/40) | 95.0% (38/40) | 100.0% (40/40) | 83.1% |
| starmie | 10.0% (4/40) | 75.0% (30/40) | 75.0% (30/40) | 75.0% (30/40) | 58.8% |

## Meta-weighted edge (usage share × matchup)

Weights from meta snapshot field chart. Panel rows without a meta mapping (currently **crustle**) are skipped for the weighted edge — they still appear in the equal-weight pool above.

| Candidate | Weighted score | Field score (usage-weighted) | Edge vs field | Coverage |
|-----------|----------------|------------------------------|---------------|----------|
| dragapult | 72.0% | 52.0% | +19.9% | 34.0% |
| starmie | 38.8% | 52.0% | -13.2% | 34.0% |

### Matchup-level edges (committed deck detail)

- vs **alakazam** (alakazam_dunsparce): our 50.0% vs field score 51.3% (usage 19.0%) → matchup edge -1.3%
- vs **spidops** (team_rocket_spidops): our 95.0% vs field score 64.1% (usage 1.2%) → matchup edge +30.9%
- vs **starmie** (starmie): our 100.0% vs field score 51.9% (usage 13.9%) → matchup edge +48.1%

## Ladder EV reference (meta snapshot, not local holdout)

- **dragapult**: usage 7.3%, field score 49.1%, matchup-weighted EV 49.5%
- **starmie**: usage 13.9%, field score 51.9%, matchup-weighted EV 53.1%

## Decision

**Committed deck: `dragapult`**

- Local holdout meta-weighted leader: dragapult (edge +0.199, weighted score 0.720).
- Ladder EV gap (Starmie − Dragapult) = +3.7% (53.1% vs 49.5%).
- Ladder EV gap < 5pp and local holdout favors Dragapult after the choose() scoping fix → commit Dragapult.
- Meta snapshot (2026-06-28) ladder EV: Starmie usage=13.9% score=51.9% EV=53.1%; Dragapult usage=7.3% score=49.1% EV=49.5%.

## Caveats

- Dragapult uses Baseline A (`DragapultPolicy`, no search) — matches Phase 3 V1.
- Starmie uses a lightweight heuristic agent, not a full public rule-based pilot; local Starmie win rates are a lower bound on what a tuned Starmie policy might achieve.
- Crustle/Spidops opponents remain random-policy; Crustle/Spidops/Starmie decks were upgraded for Phase 2 (ladder Crustle list; constructed Spidops/Starmie lists).
- Meta weights: Alakazam→alakazam_dunsparce, Spidops→team_rocket_spidops, Starmie→starmie; Crustle excluded from usage-weighted edge.
