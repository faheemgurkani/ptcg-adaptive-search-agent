#!/usr/bin/env python3
"""Fail if DragapultPolicy.choose() still crashes on a live holdout game."""

from __future__ import annotations

import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from env_paths import get_paths
from holdout_runner import (
    assert_policy_healthy,
    load_baseline_agent,
    load_deck,
    load_panel_opponent,
    play_game,
    policy_health,
)


def main() -> None:
    paths = get_paths()
    cg_parent = paths.cg_dir.parent if paths.cg_dir else None
    deck = load_deck(REPO_ROOT / "data" / "decks" / "dragapult.csv")
    agent = load_baseline_agent(
        REPO_ROOT / "notebooks" / "agents" / "main_baseline_a.py",
        deck,
        cg_parent=cg_parent,
        repo_root=paths.repo_root,
    )
    opp_deck, opp_agent = load_panel_opponent("alakazam", REPO_ROOT / "notebooks" / "holdout" / "panel")
    t0 = time.time()
    reward = play_game(agent, opp_agent, deck, opp_deck, seed=42)
    elapsed = time.time() - t0
    mod = getattr(agent, "_module", None)
    if mod is None:
        raise RuntimeError("agent wrapper has no module")
    assert_policy_healthy(mod, context="smoke vs alakazam")
    health = policy_health(mod)
    non_fb_rate = health["non_fallback"] / health["choose_ok"] if health["choose_ok"] else 0.0
    print(
        f"smoke ok reward={reward:.0f} elapsed={elapsed:.2f}s "
        f"choose_ok={health['choose_ok']} fail={health['choose_fail']} "
        f"non_fallback_rate={non_fb_rate:.3f}"
    )
    if non_fb_rate < 0.05:
        raise RuntimeError("policy still looks like first-option fallback")


if __name__ == "__main__":
    main()
