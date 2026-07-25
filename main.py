"""PTCG AI Battle Challenge agent entry point."""

from __future__ import annotations

import os

from cg.api import to_observation_class

DECK_PATHS = (
    "data/deck.csv",
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
)


def _load_deck() -> list[int]:
    file_path = next(path for path in DECK_PATHS if os.path.exists(path))

    with open(file_path, "r", encoding="utf-8") as file:
        rows = [line.strip() for line in file.read().splitlines() if line.strip()]

    if len(rows) != 60:
        raise ValueError(f"deck.csv must contain 60 card IDs, found {len(rows)}")

    return [int(card_id) for card_id in rows]


def agent(obs_dict: dict) -> list[int]:
    """Return legal option indices for the current observation."""
    obs = to_observation_class(obs_dict)

    if obs.select is None:
        return _load_deck()

    select = obs.select
    count = max(select.minCount, min(select.maxCount, len(select.option)))
    return list(range(count))
