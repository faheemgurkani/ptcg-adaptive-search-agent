"""Local holdout evaluation using kaggle-environments cabt."""

from __future__ import annotations

import hashlib
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


def paired_seed(seed_base: int, opponent: str, game_idx: int) -> int:
    """Deterministic seed shared across ablation variants.

    Does not include baseline_name (so V1–V4 play the same matchup index).
    Avoids salted builtin hash(). cabt C++ shuffle may still be unseeded
    unless the engine honors configuration.seed.
    """
    digest = hashlib.md5(f"{opponent}:{game_idx}".encode("utf-8"), usedforsecurity=False).hexdigest()
    return seed_base + (int(digest[:8], 16) % 10_000_000)


def reset_policy_counters(mod: Any) -> None:
    for name in (
        "POLICY_CHOOSE_OK",
        "POLICY_CHOOSE_FAIL",
        "POLICY_NON_FALLBACK",
        "POLICY_EMPTY_ORDER",
        "SEARCH_SIMULATE_OK",
        "SEARCH_SIMULATE_FAIL",
    ):
        if hasattr(mod, name):
            setattr(mod, name, 0)
    if hasattr(mod, "POLICY_LAST_ERROR"):
        mod.POLICY_LAST_ERROR = ""


def policy_health(mod: Any) -> dict[str, Any]:
    return {
        "choose_ok": int(getattr(mod, "POLICY_CHOOSE_OK", 0) or 0),
        "choose_fail": int(getattr(mod, "POLICY_CHOOSE_FAIL", 0) or 0),
        "non_fallback": int(getattr(mod, "POLICY_NON_FALLBACK", 0) or 0),
        "empty_order": int(getattr(mod, "POLICY_EMPTY_ORDER", 0) or 0),
        "search_ok": int(getattr(mod, "SEARCH_SIMULATE_OK", 0) or 0),
        "search_fail": int(getattr(mod, "SEARCH_SIMULATE_FAIL", 0) or 0),
        "last_error": str(getattr(mod, "POLICY_LAST_ERROR", "") or ""),
    }


def assert_policy_healthy(mod: Any, *, context: str) -> None:
    if not hasattr(mod, "POLICY_CHOOSE_OK"):
        return
    health = policy_health(mod)
    if health["choose_fail"] > 0:
        raise RuntimeError(
            f"{context}: choose() crashed {health['choose_fail']} time(s): {health['last_error']}"
        )
    if health["choose_ok"] <= 0:
        raise RuntimeError(f"{context}: choose() never succeeded")


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
    wrapped = wrap_agent(mod.agent, deck)
    wrapped._module = mod  # type: ignore[attr-defined]
    return wrapped


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
    configuration: dict[str, Any] = {"decks": [our_deck, opp_deck]}
    if seed is not None:
        configuration["seed"] = int(seed)
    env = make("cabt", configuration=configuration)
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
            seed = paired_seed(seed_base, opponent, game_idx)
            t0 = time.time()
            reward = play_game(
                our_agent,
                opp_agent,
                our_deck,
                opp_deck,
                seed=seed,
            )
            elapsed = time.time() - t0
            mod = getattr(our_agent, "_module", None)
            if game_idx == 0 and opponent == opponents[0] and mod is not None:
                assert_policy_healthy(mod, context=f"{baseline_name} vs {opponent} game 0")
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
    mod = getattr(our_agent, "_module", None)
    if mod is not None and hasattr(mod, "POLICY_CHOOSE_OK"):
        assert_policy_healthy(mod, context=f"{baseline_name} after holdout")
        health = policy_health(mod)
        for row in rows:
            if row.get("game_index") == "summary":
                row.update(health)
        print(
            f"policy health {baseline_name}: ok={health['choose_ok']} "
            f"fail={health['choose_fail']} empty_order={health.get('empty_order', 0)} "
            f"non_fallback={health['non_fallback']} "
            f"search_ok={health.get('search_ok', 0)} search_fail={health.get('search_fail', 0)}",
            file=sys.stderr,
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
