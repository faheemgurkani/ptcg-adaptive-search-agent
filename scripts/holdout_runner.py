"""Local holdout evaluation using kaggle-environments cabt."""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kaggle_environments import make

PHASE1_OPPONENTS = ("alakazam", "crustle", "spidops", "starmie")


@dataclass(frozen=True)
class MatchResult:
    baseline: str
    opponent: str
    wins: int
    losses: int
    ties: int
    game_index: int
    our_reward: float


AgentFn = Callable[[dict], list[int]]


def load_deck(path: Path) -> list[int]:
    deck = [int(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(deck) != 60:
        raise ValueError(f"{path} must contain 60 cards, got {len(deck)}")
    return deck


def load_agent_module(
    main_py: Path,
    *,
    cg_parent: Path | None = None,
    work_dir: Path | None = None,
) -> Any:
    if cg_parent is not None:
        parent = str(cg_parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)
    spec = importlib.util.spec_from_file_location(f"agent_{main_py.stem}", main_py)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {main_py}")
    mod = importlib.util.module_from_spec(spec)
    import os

    old_cwd = os.getcwd()
    try:
        os.chdir(work_dir or main_py.parent)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(old_cwd)
    if not callable(getattr(mod, "agent", None)):
        raise AttributeError(f"{main_py} has no callable agent()")
    return mod


def stage_repo_deck(deck: list[int], repo_root: Path) -> None:
    text = "\n".join(str(c) for c in deck) + "\n"
    (repo_root / "deck.csv").write_text(text, encoding="utf-8")
    data_deck = repo_root / "data" / "deck.csv"
    data_deck.parent.mkdir(parents=True, exist_ok=True)
    if not data_deck.exists():
        data_deck.write_text(text, encoding="utf-8")


def wrap_agent(agent_fn: AgentFn, deck: list[int]) -> AgentFn:
    """Ensure deck submission works even when agent reads deck.csv from disk."""

    def wrapped(obs_dict: dict) -> list[int]:
        if obs_dict.get("select") is None:
            return deck
        return agent_fn(obs_dict)

    return wrapped


def load_baseline_agent(
    main_py: Path,
    deck: list[int],
    *,
    cg_parent: Path | None = None,
    repo_root: Path | None = None,
) -> AgentFn:
    if repo_root is not None:
        stage_repo_deck(deck, repo_root)
    mod = load_agent_module(main_py, cg_parent=cg_parent, work_dir=repo_root or main_py.parent)
    return wrap_agent(mod.agent, deck)


def load_panel_opponent(name: str, panel_dir: Path) -> tuple[list[int], AgentFn]:
    opp_dir = panel_dir / name
    deck = load_deck(opp_dir / "deck.csv")
    mod = load_agent_module(opp_dir / "main.py")
    return deck, wrap_agent(mod.agent, deck)


def play_game(
    our_agent: AgentFn,
    opp_agent: AgentFn,
    our_deck: list[int],
    opp_deck: list[int],
    *,
    seed: int | None = None,
) -> float:
    if seed is not None:
        random.seed(seed)
    env = make("cabt", configuration={"decks": [our_deck, opp_deck]})
    env.run([our_agent, opp_agent])
    return float(env.steps[-1][0].reward)


def run_holdout_suite(
    *,
    baseline_name: str,
    our_agent: AgentFn,
    our_deck: list[int],
    panel_dir: Path,
    opponents: tuple[str, ...] = PHASE1_OPPONENTS,
    games: int = 40,
    seed_base: int = 42,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    summary: dict[tuple[str, str], dict[str, int]] = {}

    for opponent in opponents:
        opp_deck, opp_agent = load_panel_opponent(opponent, panel_dir)
        key = (baseline_name, opponent)
        summary[key] = {"wins": 0, "losses": 0, "ties": 0}

        for game_idx in range(games):
            seed = seed_base + hash((baseline_name, opponent, game_idx)) % 10_000_000
            t0 = time.time()
            reward = play_game(
                our_agent,
                opp_agent,
                our_deck,
                opp_deck,
                seed=seed,
            )
            elapsed = time.time() - t0
            if reward > 0:
                summary[key]["wins"] += 1
            elif reward < 0:
                summary[key]["losses"] += 1
            else:
                summary[key]["ties"] += 1
            rows.append(
                {
                    "baseline": baseline_name,
                    "opponent": opponent,
                    "game_index": game_idx,
                    "our_reward": reward,
                    "elapsed_sec": round(elapsed, 3),
                }
            )

    for (baseline, opponent), stats in summary.items():
        total = stats["wins"] + stats["losses"] + stats["ties"]
        rate = stats["wins"] / total if total else 0.0
        rows.append(
            {
                "baseline": baseline,
                "opponent": opponent,
                "game_index": "summary",
                "wins": stats["wins"],
                "losses": stats["losses"],
                "ties": stats["ties"],
                "win_rate": rate,
                "games": total,
            }
        )
    return rows


def summarize_holdout(results: list[dict[str, Any]], *, promote_threshold: float = 0.52) -> list[dict[str, Any]]:
    summaries = [r for r in results if r.get("game_index") == "summary"]
    out = []
    for row in summaries:
        rate = float(row["win_rate"])
        passed = rate >= promote_threshold
        out.append(
            {
                **row,
                "holdout_gate": "holdout_pass" if passed else "holdout_fail",
                "verdict": "PROMOTE_CANDIDATE" if passed else "HOLD_DO_NOT_SUBMIT",
            }
        )
    return out
