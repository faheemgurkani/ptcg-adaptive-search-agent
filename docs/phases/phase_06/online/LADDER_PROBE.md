# Phase 6 — Informal ladder probe

**Not** a holdout-to-ladder transfer study. Mixed downloaded episodes (`current`, `last_active`, Phase 1 A/B).

`current` (5 Dragapult-ID games): 4 still 100% first-option; 1 ~19% first-option (a non-stub policy ran). Status of record: [`../PHASE_06_STATUS.json`](../PHASE_06_STATUS.json). Raw dump: [`ladder_probe.json`](ladder_probe.json).

```json
{
  "current": {
    "n": 5,
    "wins": 1,
    "first_option_rate_mean": 0.839,
    "n_all_first_option": 4,
    "n_policy_like": 1,
    "id_kind": {
      "dragapult": 5
    },
    "episodes": [
      93412894,
      93413802,
      93414757,
      93415611,
      93416534
    ]
  },
  "last_active": {
    "n": 10,
    "wins": 4,
    "first_option_rate_mean": 0.995,
    "n_all_first_option": 9,
    "n_policy_like": 0,
    "id_kind": {
      "dragapult": 10
    },
    "episodes": [
      93210212,
      93285484,
      93299622,
      93328304,
      93402459,
      92629033,
      92970051,
      93167495,
      93409392,
      93413906
    ]
  },
  "phase1_a": {
    "n": 9,
    "wins": 3,
    "first_option_rate_mean": 0.943,
    "n_all_first_option": 7,
    "n_policy_like": 0,
    "id_kind": {
      "UNSURE": 9
    },
    "episodes": [
      88299992,
      88301029,
      88301557,
      88302605,
      88303662,
      88300519,
      88302078,
      88303144,
      88304270
    ]
  },
  "phase1_b": {
    "n": 10,
    "wins": 7,
    "first_option_rate_mean": 0.937,
    "n_all_first_option": 8,
    "n_policy_like": 0,
    "id_kind": {
      "UNSURE": 9,
      "dragapult": 1
    },
    "episodes": [
      88299983,
      88300502,
      88301549,
      88302593,
      88304240,
      88301030,
      88302072,
      88303131,
      88303651,
      88304775
    ]
  }
}
```
