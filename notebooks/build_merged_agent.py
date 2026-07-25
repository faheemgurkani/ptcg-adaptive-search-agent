"""Regenerate merged_agent_main.py from public reference notebooks.

Merge plan:
- Doc 4/8 (Dragapult): policy skeleton -> DragapultPolicy
- Doc 10 (Expectimax): Search API + UCB1 + opponent reads (_opponent_is_*)
- Docs 9/11 (Meta snapshot): not parsed here; deck/holdout handled in workbench notebook
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs" / "resources" / "reference_notebooks"
OUT = Path(__file__).with_name("merged_agent_main.py")

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
        elif pokemon.id == 721:
            op_dmg = 130 if assumed_energies >= 3 else 0
        elif pokemon.id == 723:
            op_dmg = 240 if assumed_energies >= 4 else 0
        elif pokemon.id == Dragapult_ex:
            op_dmg = 200 if assumed_energies >= 2 else 0
        else:
            op_dmg = assumed_energies * 40
        op_max_damage = max(op_max_damage, op_dmg)

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


def extract_writefile(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if "%%writefile main.py" in src:
            return src.split("%%writefile main.py\n", 1)[1]
    raise ValueError(f"No %%writefile main.py cell in {nb_path}")


def build() -> str:
    drag = extract_writefile(REF / "a-sample-rule-based-agent-dragapult-ex-deck.ipynb")
    exp = extract_writefile(REF / "improved-probabilistic-agent.ipynb")

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
        "        damage = 200\n",
        "        damage = 200\n"
        "        if _opponent_is_crustle_wall(obs, my_index):\n"
        "            damage = max(120, damage - 40)\n"
        "        if _opponent_is_water_deck(obs, my_index) and len(op_state.prize) <= 3:\n"
        "            can_main_attack = False\n",
    )

    header = textwrap.dedent(
        '''
        """Merged agent: Dragapult policy skeleton + opponent reads + UCB1 search."""
        from __future__ import annotations

        import math
        import os
        import random
        import time
        from collections import defaultdict

        from cg.api import (
            AreaType, Card, CardType, Log, LogType, Observation, OptionType, Pokemon,
            SelectContext, all_card_data, to_observation_class,
        )

        _SEARCH_OK = False
        try:
            from cg.api import search_begin, search_step
            _SEARCH_OK = True
        except Exception:
            pass

        USE_SEARCH = True
        SEARCH_TIME_BUDGET = 1.5
        SEARCH_MAX_CANDIDATES = 8
        OPP_WATER = {721, 722, 723}
        OPP_CRUSTLE = {344, 345}
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
            return _opponent_has(obs, player_index, OPP_WATER)


        def _opponent_is_crustle_wall(obs: Observation, player_index: int) -> bool:
            return _opponent_has(obs, player_index, OPP_CRUSTLE)


        class DragapultPolicy:
            """Policy skeleton from the public Dragapult rule-based notebook."""

            def __init__(self, obs: Observation):
                self.obs = obs

            def choose(self) -> list[int]:
                obs = self.obs
        '''
    )

    rollout_start = exp.index("def rollout_turn(sid, cur_obs, your_index):")
    search = exp[rollout_start:exp.index("def agent(obs_dict: dict) -> list[int]:")]
    search = search.replace("AdvancedPolicy", "DragapultPolicy")

    agent_wrapper = textwrap.dedent(
        '''

        def agent(obs_dict: dict) -> list[int]:
            try:
                obs = to_observation_class(obs_dict)
            except Exception:
                return my_deck if obs_dict.get("select") is None else [0]

            if obs.select is None:
                return my_deck

            try:
                ordered = SEARCH_ALGO(obs_dict, obs)
                if ordered is None:
                    ordered = DragapultPolicy(obs).choose()
                n = len(obs.select.option)
                ordered = [i for i in ordered if 0 <= i < n]
                if not ordered:
                    return list(range(min(max(1, obs.select.minCount), n)))
                k = max(min(obs.select.maxCount, n), min(max(1, obs.select.minCount), n))
                return ordered[:k]
            except Exception:
                n = len(obs.select.option)
                return list(range(min(max(1, obs.select.minCount), n)))
        '''
    )

    return header + "\n\n" + pre_agent + opponent + body + "\n\n" + EVALUATE_STATE + "\n\n" + search + agent_wrapper


def main() -> None:
    OUT.write_text(build())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
