# Phase 5 completion

**Status:** offline complete; per-decision detector traces deferred.

Reuse Phase 3 V1 vs V3 (panel v2, repaired policy). No new games. No weight or detector changes.

- Adaptation reduces win rate: pooled **−5.0 pp**; Crustle **−15.0 pp** (97.5% → 82.5%).
- Detectors read opponent **active + bench IDs only**. Empty board → both False (false negative until the ID appears, not a false positive).
- Panel deck lists: Crustle hits `{344,345}`; Starmie hits water `{360,361,1030,1031}`; Alakazam and Spidops hit neither.
- **Decision:** do not add Spidops/Festival detectors. The Crustle hypothesis already failed; Spidops V3 is already 40/40 without a hook.
- **Decision:** do not retune hooks this cycle — that would confound attribution.
- Per-turn fire logs are not in Phase 3 CSVs; an instrumented V3 rerun is future work.

Kaggle agent stays **V1** (adaptation off).
