"""Phase 2 Starmie candidate — lightweight heuristic (not a full rule-based pilot).

Biases toward Mega/Misty Starmie line plays, Water energy attach, evolve, and attack.
Used only for deck-selection holdout comparison against DragapultPolicy.
"""

from __future__ import annotations

import os
import random

from cg.api import Observation, OptionType, to_observation_class

DECK_PATHS = (
    "data/decks/starmie.csv",
    "data/deck.csv",
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
)

PREFERRED_CARD_IDS = {
    360,  # Misty's Staryu
    361,  # Misty's Starmie
    1030,  # Staryu
    1031,  # Mega Starmie ex
    140,  # Fezandipiti ex
    3,  # Basic Water Energy
    11,  # Mist Energy
    1086,  # Buddy-Buddy Poffin
    1121,  # Ultra Ball
    1079,  # Rare Candy
    1182,  # Boss's Orders
    1097,  # Night Stretcher
    1227,  # Lillie's Determination
}

TYPE_PRIORITY = {
    OptionType.ATTACK: 1000,
    OptionType.EVOLVE: 800,
    OptionType.ATTACH: 700,
    OptionType.ABILITY: 600,
    OptionType.PLAY: 500,
    OptionType.YES: 400,
    OptionType.CARD: 300,
    OptionType.ENERGY_CARD: 280,
    OptionType.ENERGY: 260,
    OptionType.END: 50,
    OptionType.NO: 10,
    OptionType.RETREAT: 40,
}


def _load_deck() -> list[int]:
    path = next((p for p in DECK_PATHS if os.path.exists(p)), None)
    if path is None:
        raise FileNotFoundError("No Starmie deck.csv found")
    with open(path, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
    return [int(x) for x in lines[:60]]


MY_DECK = _load_deck()


def _option_card_id(obs: Observation, opt) -> int | None:
    if getattr(opt, "cardId", None) is not None:
        return int(opt.cardId)
    if opt.area is None or opt.index is None:
        return None
    try:
        from cg.api import AreaType

        me = obs.current.players[obs.current.yourIndex]
        if opt.area == AreaType.HAND and 0 <= opt.index < len(me.hand):
            return int(me.hand[opt.index].id)
        if opt.area == AreaType.ACTIVE and me.active and 0 <= opt.index < len(me.active):
            return int(me.active[opt.index].id)
        if opt.area == AreaType.BENCH and 0 <= opt.index < len(me.bench) and me.bench[opt.index]:
            return int(me.bench[opt.index].id)
    except Exception:
        return None
    return None


def _score_option(obs: Observation, opt) -> float:
    opt_type = opt.type if isinstance(opt.type, OptionType) else OptionType(int(opt.type))
    score = float(TYPE_PRIORITY.get(opt_type, 100))
    cid = _option_card_id(obs, opt)
    if cid is not None and cid in PREFERRED_CARD_IDS:
        score += 250.0
    if opt_type == OptionType.ATTACK:
        score += 100.0
    if opt_type == OptionType.END:
        # Prefer ending only when nothing better exists (kept low).
        score -= 20.0
    return score + random.random() * 5.0


def agent(obs_dict: dict) -> list[int]:
    obs: Observation = to_observation_class(obs_dict)
    if obs.select is None:
        return MY_DECK

    n = len(obs.select.option)
    k = obs.select.maxCount
    if n == 0 or k <= 0:
        return []

    ranked = sorted(range(n), key=lambda i: _score_option(obs, obs.select.option[i]), reverse=True)
    chosen = ranked[:k]
    # Engine requires no duplicates and valid indices.
    return sorted(set(chosen))[:k]
