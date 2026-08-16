# Phase 6 — Live ladder validation

**Status: PACKAGE READY / LIVE PENDING.** See [`PHASE_06_STATUS.json`](PHASE_06_STATUS.json)

**Goal:** Confirm offline V1 results transfer to the live ladder. Submit **V1**, not V4.

## This session

- Verified `submission.tar.gz` is V1 (`USE_SEARCH=False`, `USE_OPPONENT_ADAPTATION=False`) + Dragapult `{119,120,121}`.
- Rebuilt the tarball without `__pycache__`.
- Kaggle CLI is not installed here; the competition **final submission deadline was 2026-08-16** (evaluation window 17–31 Aug). New uploads may be closed.

## Still needed (cannot finish in 30 minutes)

1. If uploads are still open: submit `submission.tar.gz` from the Kaggle UI and record peak vs equilibrium rating.
2. Download repaired-V1 episode JSONs; compare per-archetype WR to Phase 3 holdout (V1 Crustle 97.5%, Alakazam 65.0%, Spidops 97.5%, Starmie 100%).
3. Winner's-curse check on a refreshed panel — not run.

## Informal probe (not completion)

A mixed download of episodes was filed under [`online/ladder_probe.json`](online/ladder_probe.json) · [`online/LADDER_PROBE.md`](online/LADDER_PROBE.md).

`current` (5 games, Dragapult IDs): 4 still 100% first-option; 1 game ~19% first-option (policy actually choosing). That is **not** a transfer-gap table.

**Do not use Phase 1 A/B ~507 as the V1 transfer number.** Those submissions were first-option stubs on the sample-water deck.
