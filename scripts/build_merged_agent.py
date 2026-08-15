"""Regenerate merged_agent_main.py from public reference notebooks.

Merge plan:
- Doc 4/8 (Dragapult): policy skeleton -> DragapultPolicy
- Doc 10 (Expectimax): Search API + UCB1 + opponent reads (_opponent_is_*)
- Docs 9/11 (Meta snapshot): not parsed here; deck/holdout handled in workbench notebook
"""

from __future__ import annotations

import argparse
import json
import textwrap
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

try:
    import sys

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    from env_paths import get_paths

    _PATHS = get_paths()
    REF = _PATHS.ref_dir
    AGENTS_DIR = _PATHS.notebooks_dir / "agents"
except ImportError:
    REF = ROOT / "docs" / "resources" / "reference_notebooks"
    AGENTS_DIR = ROOT / "notebooks" / "agents"


@dataclass(frozen=True)
class BaselineConfig:
    name: str
    use_search: bool
    use_opponent_adaptation: bool
    doc: str


BASELINES = {
    "baseline_a": BaselineConfig(
        name="baseline_a",
        use_search=False,
        use_opponent_adaptation=False,
        doc="Baseline A — Dragapult policy only (no search, no opponent adaptation).",
    ),
    "baseline_b": BaselineConfig(
        name="baseline_b",
        use_search=True,
        use_opponent_adaptation=False,
        doc="Baseline B — Dragapult + UCB1 search (no opponent adaptation).",
    ),
    "baseline_v3": BaselineConfig(
        name="baseline_v3",
        use_search=False,
        use_opponent_adaptation=True,
        doc="Baseline V3 — Dragapult + opponent adaptation (no search).",
    ),
    "merged": BaselineConfig(
        name="merged",
        use_search=True,
        use_opponent_adaptation=True,
        doc="Full merged agent — Dragapult + search + opponent adaptation hooks.",
    ),
}

EVALUATE_STATE = '''
def evaluate_state(obs):
    """Search rollout value function adapted for the Dragapult policy skeleton."""
    st = obs.current
    if st is None:
        return 0.0

    me = st.players[st.yourIndex]
    op = st.players[1 - st.yourIndex]

    if len(me.prize) == 0:
        return 9999999.0
    if len(op.prize) == 0:
        return -9999999.0

    val = (len(op.prize) - len(me.prize)) * 10000.0
    op_board = [op.active[0] if op.active else None] + list(op.bench)
    my_board = [me.active[0] if me.active else None] + list(me.bench)

    is_crustle = any(p is not None and p.id in OPP_CRUSTLE for p in op_board)
    is_stall = is_crustle or any(p is not None and p.id == 143 for p in op_board)

    for pokemon in my_board:
        if pokemon is None:
            continue
        val += len(pokemon.energies) * 200.0
        if pokemon.id == Dragapult_ex:
            val += 1500.0 if is_crustle else 500.0
        elif pokemon.id == Drakloak:
            val += 800.0 if is_crustle else 300.0
        elif pokemon.id == Dreepy:
            val += 400.0 if is_crustle else 100.0

    if is_crustle:
        for card in me.hand:
            if card.id == Drakloak:
                val += 500.0
            elif card.id == Dreepy:
                val += 300.0

    if me.active and me.active[0] is not None:
        val += me.active[0].hp * 2.0
        if len(me.active[0].energies) >= 2:
            val += 500.0

    op_max_damage = 0
    for pokemon in op_board:
        if pokemon is None:
            continue
        val -= pokemon.hp * 1.5
        assumed_energies = len(pokemon.energies) + 1
        if pokemon.id == 678:
            op_dmg = 270 if assumed_energies >= 2 else 130 if assumed_energies >= 1 else 0
        elif pokemon.id == 674:
            op_dmg = 210 if assumed_energies >= 3 else 0
        elif pokemon.id in (721, 723, 360, 361, 1030, 1031):
            op_dmg = 240 if assumed_energies >= 2 else 130 if assumed_energies >= 1 else 0
        elif pokemon.id == Dragapult_ex:
            op_dmg = 200 if assumed_energies >= 2 else 0
        else:
            op_dmg = assumed_energies * 40
        op_max_damage = max(op_max_damage, op_dmg)

    if is_crustle and me.active and me.active[0] is not None and me.active[0].id == 235:
        val -= 8000.0

    if me.active and me.active[0] is not None:
        my_active = me.active[0]
        if op_max_damage >= my_active.hp:
            prize_risk = 2 if my_active.id == Dragapult_ex else 1
            val -= prize_risk * 4000.0
        elif op_max_damage > 0:
            val -= op_max_damage * 1.5

    deck_c = getattr(me, "deckCount", 60)
    hand_c = getattr(me, "handCount", len(me.hand))
    if is_stall:
        val += deck_c * 30.0 + hand_c * 2.0
    else:
        val += hand_c * 10.0
    if deck_c < 5:
        val -= 10000.0
    return val
'''.strip()


SEARCH_IMPL = '''
def _unwrap_search(result):
    if result is None:
        return None
    if getattr(result, "observation", None) is not None and hasattr(result, "searchId"):
        return result
    nested = getattr(result, "state", None)
    if nested is not None and getattr(nested, "observation", None) is not None:
        return nested
    return None


def _fill_ids(n, pool):
    n = int(n or 0)
    if n <= 0:
        return []
    src = [int(x) for x in pool if x is not None]
    if not src:
        src = list(my_deck) if my_deck else [1, 119]
    if len(src) >= n:
        return random.sample(src, n) if len(src) > n else list(src)
    out = list(src)
    pad = [1, 119]
    i = 0
    while len(out) < n:
        out.append(pad[i % len(pad)])
        i += 1
    return out


def _known_player_ids(player):
    ids = []
    for zone in (getattr(player, "active", None), getattr(player, "bench", None),
                 getattr(player, "hand", None), getattr(player, "discard", None)):
        for card in zone or []:
            if card is None:
                continue
            cid = getattr(card, "id", None)
            if cid is not None:
                ids.append(int(cid))
            for energy in getattr(card, "energies", None) or []:
                eid = energy if isinstance(energy, int) else getattr(energy, "id", None)
                if eid is not None:
                    ids.append(int(eid))
    return ids


def _remaining_from_list(known):
    remaining = list(my_deck)
    for kid in known:
        try:
            remaining.remove(int(kid))
        except ValueError:
            pass
    return remaining


def _search_begin_hidden(obs):
    state = obs.current
    yi = state.yourIndex
    me = state.players[yi]
    op = state.players[1 - yi]
    remaining = _remaining_from_list(_known_player_ids(me))
    your_deck = _fill_ids(getattr(me, "deckCount", 0), remaining or my_deck)
    prize_n = len(me.prize or [])
    if prize and len(prize) >= prize_n:
        your_prize = [int(x) for x in prize[:prize_n]]
    else:
        face = []
        for card in me.prize or []:
            cid = getattr(card, "id", None) if card is not None else None
            if cid is not None:
                face.append(int(cid))
        your_prize = _fill_ids(prize_n, face or remaining or my_deck)
    opponent_deck = _fill_ids(getattr(op, "deckCount", 0), [119, 1])
    opponent_prize = _fill_ids(len(op.prize or []), [1])
    opponent_hand = _fill_ids(getattr(op, "handCount", 0), [1, 119])
    opponent_active = []
    active = op.active or []
    if len(active) > 0 and active[0] is None:
        opponent_active = [119]
    return search_begin(
        obs,
        your_deck=your_deck,
        your_prize=your_prize,
        opponent_deck=opponent_deck,
        opponent_prize=opponent_prize,
        opponent_hand=opponent_hand,
        opponent_active=opponent_active,
    )


def rollout_turn(sid, cur_obs, your_index):
    steps = 0
    while steps < 20:
        if cur_obs.current is None:
            break
        if cur_obs.current.result is not None and cur_obs.current.result != -1:
            break
        if cur_obs.current.yourIndex != your_index:
            break
        if cur_obs.select is None:
            break
        if cur_obs.select.context != SelectContext.MAIN:
            sub = DragapultPolicy(cur_obs).choose()
            sel = sub[: max(1, cur_obs.select.minCount)]
        else:
            nxt = DragapultPolicy(cur_obs).choose()
            if not nxt:
                break
            sel = [nxt[0]]
            if cur_obs.select.option[nxt[0]].type == OptionType.END:
                search_step(sid, sel)
                break
        ar = search_step(sid, sel)
        nxt = _unwrap_search(ar)
        if nxt is None:
            break
        cur_obs, sid = nxt.observation, nxt.searchId
        steps += 1
    return cur_obs


def simulate_action(obs, action):
    global SEARCH_SIMULATE_OK, SEARCH_SIMULATE_FAIL
    try:
        sbi = _search_begin_hidden(obs)
        nxt = _unwrap_search(sbi)
        if nxt is None:
            SEARCH_SIMULATE_FAIL += 1
            return -float("inf")
        ar = search_step(nxt.searchId, [action])
        stepped = _unwrap_search(ar)
        if stepped is None:
            SEARCH_SIMULATE_FAIL += 1
            return -float("inf")
        cur = rollout_turn(stepped.searchId, stepped.observation, obs.current.yourIndex)
        SEARCH_SIMULATE_OK += 1
        return evaluate_state(cur)
    except Exception:
        SEARCH_SIMULATE_FAIL += 1
        return -float("inf")
    finally:
        try:
            search_end()
        except Exception:
            pass


def SEARCH_ALGO(obs_dict, obs):
    if not (_SEARCH_OK and USE_SEARCH):
        return None
    select = obs.select
    if select is None or select.context != SelectContext.MAIN:
        return None
    t0 = time.time()
    budget = float(os.environ.get("PTCG_SEARCH_TIME_BUDGET", SEARCH_TIME_BUDGET))

    base_order = DragapultPolicy(obs).choose()
    candidates = base_order[:SEARCH_MAX_CANDIDATES]
    if not candidates:
        return None
    if len(candidates) == 1:
        return [candidates[0]] + [i for i in base_order if i != candidates[0]]

    visits = {a: 0 for a in candidates}
    total_val = {a: 0.0 for a in candidates}

    try:
        for a in candidates:
            if time.time() - t0 > budget:
                break
            val = simulate_action(obs, a)
            if val != -float("inf"):
                visits[a] += 1
                total_val[a] += val

        while time.time() - t0 < budget:
            total_visits = sum(visits.values())
            if total_visits == 0:
                break
            valid_scores = [total_val[a] / visits[a] for a in candidates if visits[a] > 0]
            if not valid_scores:
                break
            min_s = min(valid_scores)
            max_s = max(valid_scores)
            if max_s == min_s:
                max_s = min_s + 1.0

            best_ucb, best_a = -float("inf"), candidates[0]
            for a in candidates:
                if visits[a] == 0:
                    best_a = a
                    break
                avg = total_val[a] / visits[a]
                norm_avg = (avg - min_s) / (max_s - min_s)
                ucb = norm_avg + 0.5 * math.sqrt(math.log(total_visits) / visits[a])
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_a = a

            val = simulate_action(obs, best_a)
            if val != -float("inf"):
                visits[best_a] += 1
                total_val[best_a] += val

        best_action = max(
            candidates,
            key=lambda a: total_val[a] / visits[a] if visits[a] > 0 else -float("inf"),
        )
        return [best_action] + [i for i in base_order if i != best_action]
    except Exception:
        return None
'''.strip()


def extract_writefile(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if "%%writefile main.py" in src:
            return src.split("%%writefile main.py\n", 1)[1]
    raise ValueError(f"No %%writefile main.py cell in {nb_path}")


def build(config: BaselineConfig = BASELINES["merged"]) -> str:
    drag = extract_writefile(REF / "a-sample-rule-based-agent-dragapult-ex-deck.ipynb")

    agent_idx = drag.index("def agent(obs_dict: dict) -> list[int]:")
    pre_agent = drag[:agent_idx]
    agent_src = drag[agent_idx:]

    pre_agent = pre_agent.replace(
        """# Load deck.csv in the dataset
file_path = "deck.csv"
if not os.path.exists(file_path):
    file_path = "/kaggle_simulations/agent/" + file_path
with open(file_path, "r") as file:
    csv = file.read().split("\\n")
my_deck = []
for i in range(60):
    my_deck.append(int(csv[i]))
    """,
        """DECK_PATHS = (
    "data/deck.csv",
    "data/pokemon-tcg-ai-battle/sample_submission/sample_submission/deck.csv",
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
)
file_path = next(path for path in DECK_PATHS if os.path.exists(path))
with open(file_path, "r", encoding="utf-8") as file:
    csv = [line.strip() for line in file.read().splitlines() if line.strip()]
my_deck = [int(csv[i]) for i in range(60)]
""",
    )

    start = agent_src.index("    state = obs.current\n")
    end = agent_src.index("    return output\n") + len("    return output\n")
    body = textwrap.indent(agent_src[start:end], "    ")
    body = body.replace(
        "        do_switch = (not can_main_attack and (bench_attacker or (active_id != Budew and field_counts[Budew] >= 1 and state.turn >= 2)))\n",
        "        do_switch = (not can_main_attack and (bench_attacker or (active_id != Budew and field_counts[Budew] >= 1 and state.turn >= 2)))\n"
        "        if USE_OPPONENT_ADAPTATION and _opponent_is_crustle_wall(obs, my_index) and active_id == Budew:\n"
        "            do_switch = True\n",
    )
    body = body.replace(
            "            elif o.type == OptionType.ATTACK:\n"
            "                score = o.attackId\n",
            "            elif o.type == OptionType.ATTACK:\n"
            "                score = (20000 + o.attackId) if can_main_attack else o.attackId\n",
        )
    body = body.replace(
            "            for i in range(select.maxCount):\n",
            "            for i in range(len(sorted_scores)):\n",
        )

    header = textwrap.dedent(
        f'''
        """{config.doc}"""
        from __future__ import annotations

        import math
        import os
        import random
        import sys
        import time
        import traceback
        from collections import defaultdict

        from cg.api import (
            AreaType, Card, CardType, Log, LogType, Observation, OptionType, Pokemon,
            SelectContext, all_card_data, to_observation_class,
        )

        _SEARCH_OK = False
        search_end = lambda: None
        try:
            from cg.api import search_begin, search_step, search_end
            _SEARCH_OK = True
        except Exception:
            pass

        USE_SEARCH = {config.use_search!r}
        USE_OPPONENT_ADAPTATION = {config.use_opponent_adaptation!r}
        SEARCH_TIME_BUDGET = 1.5
        SEARCH_MAX_CANDIDATES = 8
        OPP_WATER = {{721, 722, 723, 360, 361, 1030, 1031}}
        OPP_CRUSTLE = {{344, 345}}
        POLICY_CHOOSE_OK = 0
        POLICY_CHOOSE_FAIL = 0
        POLICY_NON_FALLBACK = 0
        POLICY_LAST_ERROR = ""
        SEARCH_SIMULATE_OK = 0
        SEARCH_SIMULATE_FAIL = 0
        '''
    ).strip("\n")

    opponent = textwrap.dedent(
        '''

        def _opponent_board(obs: Observation, player_index: int):
            opponent = obs.current.players[1 - player_index]
            return opponent.active + opponent.bench


        def _opponent_has(obs: Observation, player_index: int, ids: set[int]) -> bool:
            return any(p is not None and p.id in ids for p in _opponent_board(obs, player_index))


        def _opponent_is_water_deck(obs: Observation, player_index: int) -> bool:
            if not USE_OPPONENT_ADAPTATION:
                return False
            return _opponent_has(obs, player_index, OPP_WATER)


        def _opponent_is_crustle_wall(obs: Observation, player_index: int) -> bool:
            if not USE_OPPONENT_ADAPTATION:
                return False
            return _opponent_has(obs, player_index, OPP_CRUSTLE)


        class DragapultPolicy:
            """Policy skeleton from the public Dragapult rule-based notebook."""

            def __init__(self, obs: Observation):
                self.obs = obs

            def choose(self) -> list[int]:
                global pre_turn_log, current_turn_log, prize, bench_attacker
                global can_main_attack, can_switch, can_attack, can_energy_attach, use_support
                obs = self.obs
        '''
    )

    agent_wrapper = textwrap.dedent(
        '''

        def agent(obs_dict: dict) -> list[int]:
            global POLICY_CHOOSE_OK, POLICY_CHOOSE_FAIL, POLICY_NON_FALLBACK, POLICY_LAST_ERROR
            try:
                obs = to_observation_class(obs_dict)
            except Exception:
                return my_deck if obs_dict.get("select") is None else [0]

            if obs.select is None:
                return my_deck

            n = len(obs.select.option)
            fallback = list(range(min(max(1, obs.select.minCount), n))) if n else [0]
            try:
                ordered = SEARCH_ALGO(obs_dict, obs)
                if ordered is None:
                    ordered = DragapultPolicy(obs).choose()
                ordered = [i for i in ordered if 0 <= i < n]
                if not ordered:
                    print("policy returned empty action list", file=sys.stderr)
                    return fallback
                k = max(min(obs.select.maxCount, n), min(max(1, obs.select.minCount), n))
                chosen = ordered[:k]
                POLICY_CHOOSE_OK += 1
                if chosen != fallback:
                    POLICY_NON_FALLBACK += 1
                return chosen
            except Exception as exc:
                POLICY_CHOOSE_FAIL += 1
                POLICY_LAST_ERROR = f"{type(exc).__name__}: {exc}"
                traceback.print_exc(file=sys.stderr)
                return fallback
        '''
    )

    return (
        header
        + "\n\n"
        + pre_agent
        + opponent
        + body
        + "\n\n"
        + EVALUATE_STATE
        + "\n\n"
        + SEARCH_IMPL
        + agent_wrapper
    )


def output_path(config: BaselineConfig) -> Path:
    if config.name == "merged":
        try:
            return _PATHS.merged_main_py
        except NameError:
            return ROOT / "notebooks" / "merged_agent_main.py"
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    return AGENTS_DIR / f"main_{config.name}.py"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build merged agent variants.")
    parser.add_argument(
        "--variant",
        choices=[*BASELINES.keys(), "all"],
        default="all",
        help="Which agent variant to build (default: all).",
    )
    args = parser.parse_args()
    targets = BASELINES.values() if args.variant == "all" else [BASELINES[args.variant]]
    for cfg in targets:
        out = output_path(cfg)
        out.write_text(build(cfg), encoding="utf-8")
        print(f"Wrote {out}")
    if args.variant in ("merged", "all"):
        merged = output_path(BASELINES["merged"])
        text = merged.read_text(encoding="utf-8")
        root_main = ROOT / "main.py"
        root_main.write_text(text, encoding="utf-8")
        print(f"Synced {root_main}")
        AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        agents_merged = AGENTS_DIR / "main_baseline_merged.py"
        agents_merged.write_text(text, encoding="utf-8")
        print(f"Synced {agents_merged}")


if __name__ == "__main__":
    main()
