"""Baseline A — Dragapult policy only (no search, no opponent adaptation)."""
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

USE_SEARCH = False
USE_OPPONENT_ADAPTATION = False
SEARCH_TIME_BUDGET = 1.5
SEARCH_MAX_CANDIDATES = 8
OPP_WATER = {721, 722, 723, 360, 361, 1030, 1031}
OPP_CRUSTLE = {344, 345}
POLICY_CHOOSE_OK = 0
POLICY_CHOOSE_FAIL = 0
POLICY_NON_FALLBACK = 0
POLICY_LAST_ERROR = ""

import os
import sys
from collections import defaultdict

from cg.api import AreaType, CardType, Log, LogType, Observation, SelectContext, OptionType, Card, Pokemon, State, all_card_data, to_observation_class

"""
Dragapult ex Deck
Advanced Level
This deck focuses on setting up multiple knockouts to take at least three Prize cards in a single turn with its Phantom Dive attack.
"""

DECK_PATHS = (
    "data/deck.csv",
    "data/pokemon-tcg-ai-battle/sample_submission/sample_submission/deck.csv",
    "deck.csv",
    "/kaggle_simulations/agent/deck.csv",
)
file_path = next(path for path in DECK_PATHS if os.path.exists(path))
with open(file_path, "r", encoding="utf-8") as file:
    csv = [line.strip() for line in file.read().splitlines() if line.strip()]
my_deck = [int(csv[i]) for i in range(60)]

# Load all card data from the API's helper function
all_card = all_card_data()
# Create a lookup table (dictionary) to quickly access card data by its cardId
card_table = {c.cardId:c for c in all_card}

# Decklist
Dreepy = 119  # ×4
Drakloak = 120  # ×4
Dragapult_ex = 121  # ×3
Fezandipiti_ex = 140  # ×1
Latias_ex = 184  # ×1
Budew = 235  # ×2
Meowth_ex = 1071  # ×1
Rare_Candy = 1079  # ×2
Unfair_Stamp = 1080  # ×1
Buddy_Buddy_Poffin = 1086  # ×4
Night_Stretcher = 1097  # ×2
Crushing_Hammer = 1120  # ×4
Ultra_Ball = 1121  # ×4
Poke_Pad = 1152  # x3
Lucky_Helmet = 1156  # ×1
Boss_Orders = 1182  # ×3
Crispin = 1198  # ×4
Brock_Scouting = 1210  # ×2
Lillie_Determination = 1227  # ×4
Team_Rocket_Watchtower = 1256  # ×2
Basic_Fire_Energy = 2  # ×4
Basic_Psychic_Energy = 5  # ×4

UNNECESSARY = -10000000

class AttackPlan:
    attack: int = 0
    counter: list[int] = []

can_switch = False
can_attack = False
can_main_attack = False
can_energy_attach = False
use_support = 0  # The Supporter card planned for use.
bench_attacker = False  # Whether there is a Benched Pokémon that is ready to attack
pre_turn_log: list[Log] = []
current_turn_log: list[Log] = []

prize: list[int] = []
card_counts: defaultdict[int, int] = defaultdict(int)
serial_set: set[int] = set()
plan_a = AttackPlan()
plan_b = AttackPlan()


def no_damage_dex(id: int) -> bool:
    """Checks if the defending Pokémon possesses innate immunities preventing Dragapult ex from hitting it."""
    # Drednaw, Milotic ex, Sylveon, Crustle
    return id == 158 or id == 207 or id == 330 or id == 345


def no_damage_counter(pokemon: Pokemon) -> bool:
    """Checks if a target prevents placement of Phantom Dive's 6 bench damage counters (via abilities/Energy)."""
    # Poltchageist, Empoleon ex, Skeledirge, Milotic ex, Misty's Magikarp, Antique Cover Fossil
    if pokemon.id == 28 or pokemon.id == 199 or pokemon.id == 203 or pokemon.id == 207 or pokemon.id == 362 or pokemon.id == 1136:
        return True
    for card in pokemon.energyCards:
        # Mist Energy, Rock Fighting Energy
        if card.id == 11 or card.id == 20:
            return True
    return False


def prize_count(pokemon: Pokemon, is_attack_damage: bool) -> int:
    """Calculates how many Prize cards a Pokémon yields upon being Knocked Out, factoring in modifiers."""
    data = card_table[pokemon.id]
    count = 3 if data.megaEx else 2 if data.ex else 1
    if is_attack_damage:
        for card in pokemon.energyCards:
            if card.id == 12:  # Legacy Energy
                count -= 1
        for card in pokemon.tools:
            if card.id == 1172 and "Lillie" in data.name:  # Lillie’s Pearl
                count -= 1
    return max(0, count)


def pokemon_score(pokemon: Pokemon, is_attack_damage: bool) -> int:
    """Heuristically evaluates the tactical worth of targeting a specific Pokémon on the opponent's field."""
    data = card_table[pokemon.id]
    score = prize_count(pokemon, is_attack_damage) * 1000
    score += len(pokemon.energies) * 150
    score += len(pokemon.tools) * 100
    if data.stage2:
        score += 250
    elif data.stage1:
        score += 130
    
    id = pokemon.id
    # Noctowl, Fan Rotom, Archaludon ex, Meowth ex
    if id == 173 or id == 174 or id == 190 or id == 1071:
        score -= 200
    if id == 112 and len(pokemon.energies) >= 1:  # Munkidori
        score += 300
    score += pokemon.hp
    return score


def add_card_count(card: Card | Pokemon | None, my_index: int):
    if card == None:
        return
    if isinstance(card, Pokemon) or card.playerIndex == my_index:
        if card.serial not in serial_set:
            card_counts[card.id] -= 1
            serial_set.add(card.serial)
    if isinstance(card, Pokemon):
        for c in card.energyCards:
            add_card_count(c, my_index)
        for c in card.tools:
            add_card_count(c, my_index)
        for c in card.preEvolution:
            add_card_count(c, my_index)

def set_card_counts(obs: Observation, my_index: int):
    card_counts.clear()
    serial_set.clear()
    for id in my_deck:
        card_counts[id] += 1
    
    state = obs.current
    my_state = state.players[my_index]
    for card in my_state.hand:
        add_card_count(card, my_index)
    for card in my_state.discard:
        add_card_count(card, my_index)
    for card in my_state.bench:
        add_card_count(card, my_index)
    for card in my_state.active:
        add_card_count(card, my_index)
    for card in state.stadium:
        add_card_count(card, my_index)
    if state.looking != None:
        for card in state.looking:
            add_card_count(card, my_index)
    add_card_count(obs.select.effect, my_index)

    
def get_card(obs: Observation, area: AreaType, index: int, player_index: int) -> Pokemon | Card | None:
    """Helper function to safely extract a Card or Pokemon object from specific zones."""
    ps = obs.current.players[player_index]
    match area:
        case AreaType.DECK:
            return obs.select.deck[index]
        case AreaType.HAND:
            return ps.hand[index]
        case AreaType.DISCARD:
            return ps.discard[index]
        case AreaType.ACTIVE:
            return ps.active[index]
        case AreaType.BENCH:
            return ps.bench[index]
        case AreaType.PRIZE:
            return ps.prize[index]
        case AreaType.STADIUM:
            return obs.current.stadium[index]
        case AreaType.LOOKING:
            return obs.current.looking[index]
        case _:
            return None

def main_option_proc(obs: Observation, damage: int):
    state = obs.current
    select = obs.select
    my_index = state.yourIndex
    my_state = state.players[my_index]
    op_state = state.players[1 - my_index]

    global can_switch
    global can_attack
    global can_main_attack
    global can_energy_attach

    can_switch = False
    can_attack = False
    can_main_attack = False
    can_energy_attach = False
    for o in select.option:
        if o.type == OptionType.RETREAT:
            can_switch = True
        elif o.type == OptionType.ATTACK:
            can_attack = True
            if o.attackId == 154:  # Phantom Dive
                can_main_attack = True
    
    plan_a.attack = -1
    plan_b.attack = -1
    if not can_main_attack and not (bench_attacker and can_switch):
        return
    
    cards = [op_state.active[0]]
    for pokemon in op_state.bench:
        cards.append(pokemon)
    counter_indices = []
    ci = []
    ci.append(0)
    remain_damage = 60
    while ci:
        index = ci[-1]
        hp = cards[index].hp
        if remain_damage >= hp:
            counter_indices.append(ci.copy())
            if index < len(cards) - 1:
                remain_damage -= hp
                ci.append(index + 1)
                continue
        if index == len(cards) - 1:
            ci.pop()
            if ci:
                remain_damage += cards[ci[-1]].hp
        if ci:
            ci[-1] += 1
    counter_indices.append([])

    remain_prize = len(my_state.prize)
    plan_score = 0
    for i, pokemon in enumerate(cards):
        base_prize_count = 0
        base_score = pokemon_score(pokemon, True)
        active_damage = 0 if no_damage_dex(pokemon.id) else damage
        if pokemon.hp <= active_damage:
            base_prize_count += prize_count(pokemon, True)
        else:
            base_score *= active_damage / pokemon.hp
        ci = []
        max_score = base_score
        if remain_prize <= base_prize_count:
            max_score = 50000
        else:
            for indices in counter_indices:
                if i in indices:
                    continue
                prize = base_prize_count
                score = base_score
                for index in indices:
                    prize += prize_count(cards[index], False)
                    score += pokemon_score(cards[index], False)
                if remain_prize <= prize:
                    score = 50000
                else:
                    if prize >= 2:
                        if remain_prize <= 4:
                            score -= 1200
                    elif prize == 1:
                        score -= 300
                    else:
                        score += 1200
                if max_score < score:
                    max_score = score
                    ci = indices
        if plan_score < max_score:
            plan_score = max_score
            plan_a.attack = i
            plan_a.counter = ci
        if i == 0:
            plan_b.attack = plan_a.attack
            plan_b.counter = plan_a.counter



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
        state = obs.current
        select = obs.select
        context = select.context
        my_index = state.yourIndex
        my_state = state.players[my_index]
        op_state = state.players[1 - my_index]
            
        if state.turn == 0:
            prize.clear()
            pre_turn_log.clear()
            current_turn_log.clear()
        else:
            for log in obs.logs:
                current_turn_log.append(log)
                if log.type == LogType.TURN_END:
                    pre_turn_log = current_turn_log
                    current_turn_log = []

        pre_ko = False
        no_item = False
        for log in pre_turn_log:
            if log.type == LogType.ATTACK:
                if log.attackId == 323:  # Itchy Pollen
                    no_item = True
            elif log.type == LogType.MOVE_CARD:
                if (log.playerIndex == my_index
                    and (log.fromArea == AreaType.BENCH or log.fromArea == AreaType.ACTIVE)
                    and log.toArea == AreaType.DISCARD):
                    pre_ko = True

        if select.deck != None:
            set_card_counts(obs, my_index)
            for card in select.deck:
                card_counts[card.id] -= 1
            prize.clear()
            for id in card_counts:
                for _ in range(card_counts[id]):
                    prize.append(id)
                
        set_card_counts(obs, my_index)
        for id in prize:
            card_counts[id] -= 1
        deck_counts = card_counts

        prize_diff = len(my_state.prize) - len(op_state.prize)
    
        global bench_attacker

        # Number of cards per card ID on the Bench and in the Active Spot
        field_counts = defaultdict(int)
        # Number of cards per card ID in hand
        hand_counts = defaultdict(int)
        # Number of cards per card ID in discard pile
        discard_counts = defaultdict(int)
    
        active_id = 0
        bench_attacker = False
        can_evolve_dreepy = False
        evolve_dreepy_count = 0
        can_evolve_drakloak = False
        damage = 200
        for card in my_state.active:
            if card == None:
                continue
            active_id = card.id
            field_counts[card.id] += 1
            if not card.appearThisTurn:
                if card.id == Dreepy:
                    can_evolve_dreepy = True
                    evolve_dreepy_count += 1
                elif card.id == Drakloak:
                    can_evolve_drakloak = True
        for card in my_state.bench:
            field_counts[card.id] += 1
            if not card.appearThisTurn:
                if card.id == Dreepy:
                    can_evolve_dreepy = True
                    evolve_dreepy_count += 1
                elif card.id == Drakloak:
                    can_evolve_drakloak = True
            if card.id == Dragapult_ex and len(card.energies) >= 2:
                bench_attacker = True
        main_pokemon_count = field_counts[Dreepy] + field_counts[Drakloak] + field_counts[Dragapult_ex]
        no_more_dex = (field_counts[Dragapult_ex] * 2 >= len(op_state.prize))

        stadium_id = 0
        for card in state.stadium:
            stadium_id = card.id

        support_count = 0

        for card in my_state.discard:
            discard_counts[card.id] += 1

        def attach_score(attach_id: int, pokemon: Pokemon, active: bool) -> int:
            energy_count = len(pokemon.energies)
            if card_table[attach_id].cardType == CardType.TOOL:
                # Attach tool
                score = 60000
                if active:
                    score += 1000
                return score
        
            # Attach energy
            if pokemon.id == Budew:
                return -1
            elif pokemon.id == Meowth_ex or pokemon.id == Fezandipiti_ex or pokemon.id == Latias_ex:
                if active and not can_switch and not my_state.asleep and not my_state.paralyzed:
                    if bench_attacker or field_counts[Budew] >= 1:
                        return 22000
                    else:
                        return 18000
                else:
                    return -1
            if active and can_main_attack:
                return -1
            score = 20000
            if energy_count >= 2:
                if active and not can_switch and not my_state.asleep and not my_state.paralyzed:
                    score += 200
                else:
                    return -1
            elif energy_count == 1:
                if attach_id == pokemon.energyCards[0].id:
                    return -1
                if pokemon.id == Dragapult_ex:
                    score += 250
                elif pokemon.id == Dreepy:
                    score -= 150
                else:
                    score -= 200
                if active:
                    score += 200
            else:  # energy_count == 0
                if active:
                    if bench_attacker:
                        score += 400
                else:
                    if pokemon.id == Dragapult_ex:
                        score += 150
                    elif pokemon.id == Dreepy:
                        score += 100
                    else:
                        score += 50
                    if bench_attacker:
                        score -= 200
            if no_more_dex and (pokemon.id == Dreepy or pokemon.id == Drakloak):
                score -= 500
            return score
    
        def hand_score(id: int, ignore_count: bool):
            score = 0
            if id == Dreepy:
                if main_pokemon_count >= 3:
                    score = 1000
                else:
                    score = 18000
            elif id == Drakloak:
                if can_evolve_dreepy:
                    score = 20000
                else:
                    score = 3000
            elif id == Dragapult_ex:
                if no_more_dex:
                    score = UNNECESSARY
                elif can_evolve_dreepy and hand_counts[Rare_Candy] >= 1 and not no_item:
                    score = 40000
                elif can_evolve_drakloak:
                    if field_counts[id] == 0:
                        score = 30000
                    elif field_counts[id] == 1:
                        score = 10000
                    else:
                        score = 50
                else:
                    if field_counts[id] >= 2:
                        score = 50
                    else:
                        score = 2000
            elif id == Fezandipiti_ex:
                if pre_ko:
                    score = 50000
                elif prize_diff <= -2:
                    score = 5
                elif len(op_state.prize) == 1:
                    score = UNNECESSARY
            elif id == Latias_ex:
                if active_id == Fezandipiti_ex or active_id == Meowth_ex or active_id == Dreepy:
                    if field_counts[Drakloak] + field_counts[Dragapult_ex] == 0:
                        score = 28000
                    else:
                        score = 15000
                else:
                    score = 10
            elif id == Budew:
                if field_counts[id] + field_counts[Drakloak] + field_counts[Dragapult_ex] >= 1:
                    score = UNNECESSARY
                elif state.turn >= 2:
                    score = 30000
            elif id == Meowth_ex:
                if support_count > hand_counts[Boss_Orders] or stadium_id == Team_Rocket_Watchtower:
                    score = 5
                elif state.supporterPlayed:
                    score = 40
                else:
                    score = 35000
            elif id == Rare_Candy:
                if no_more_dex:
                    score = UNNECESSARY
                elif can_evolve_dreepy and hand_counts[Dragapult_ex] >= 1:
                    score = 40000
            elif id == Unfair_Stamp:
                if pre_ko:
                    score = 80000
                elif len(op_state.prize) == 1:
                    score = UNNECESSARY
                else:
                    score = 80
            elif id == Buddy_Buddy_Poffin:
                count = deck_counts[Dreepy]
                if count == 0:
                    score = UNNECESSARY
                else:
                    if state.turn <= 2 and field_counts[Budew] == 0 and deck_counts[Budew] >= 1:
                        count += 1
                    if count >= 2:
                        score = 35000
            elif id == Night_Stretcher:
                for i in discard_counts:
                    if discard_counts[i] >= 1:
                        card_type = card_table[i].cardType
                        if card_type == CardType.POKEMON or card_type == CardType.BASIC_ENERGY:
                            score = max(score, hand_score(i, ignore_count))
            elif id == Crushing_Hammer:
                score = 20
            elif id == Ultra_Ball:
                if main_pokemon_count <= 2 or field_counts[Dreepy] >= 1:
                    score = 70
                else:
                    score = 5
            elif id == Poke_Pad:
                score = max(hand_score(Dreepy, ignore_count), hand_score(Drakloak, ignore_count))
            elif id == Lucky_Helmet:
                score = 15
            elif id == Boss_Orders:
                if plan_a.attack > 0:
                    score = 60000
            elif id == Crispin:
                if not ignore_count or support_count == 0:
                    if deck_counts[Basic_Fire_Energy] == 0 or deck_counts[Basic_Psychic_Energy] == 0:
                        score = 10
                    if not can_main_attack and not bench_attacker and field_counts[Dragapult_ex] >= 1:
                        score = 55000
                    else:
                        score = 25000
            elif id == Brock_Scouting:
                if not ignore_count or support_count == 0:
                    if state.turn == 2 and field_counts[Budew] + field_counts[Latias_ex] == 0:
                        score = 50000
                    else:
                        score = 30000
            elif id == Lillie_Determination:
                if not ignore_count or support_count == 0:
                    score = 45000
            elif id == Team_Rocket_Watchtower:
                if stadium_id != 0 and stadium_id != Team_Rocket_Watchtower:
                    score = 4000
            elif id == Basic_Fire_Energy or id == Basic_Psychic_Energy:
                if can_main_attack and (len(op_state.prize) <= 2
                    or (bench_attacker and len(op_state.prize) <= 4)):
                    score = UNNECESSARY
                else:
                    max_score = -10000
                    for pokemon in my_state.active:
                        if pokemon == None:
                            continue
                        max_score = max(max_score, attach_score(id, pokemon, True))
                    for pokemon in my_state.bench:
                        max_score = max(max_score, attach_score(id, pokemon, False))
                    score = max_score - 5000
                    if can_main_attack or bench_attacker:
                        score /= 10
        
            if not ignore_count and hand_counts[id] > 0:
                if id == Drakloak and hand_counts[id] < evolve_dreepy_count:
                    score -= 10
                elif id == Dreepy:
                    score -= 100
                else:
                    score -= 100000
            return score

        global use_support
        if context == SelectContext.MAIN:
            main_option_proc(obs, damage)
                    
            use_support = 0
            if not state.supporterPlayed:
                support_score = 0
                for o in select.option:
                    if o.type == OptionType.PLAY:
                        card = get_card(obs, AreaType.HAND, o.index, state.yourIndex)
                        if card_table[card.id].cardType == CardType.SUPPORTER:
                            score = hand_score(card.id, True)
                            if support_score < score:
                                support_score = score
                                use_support = card.id

        hand_scores = []
        negative_hand_count = 0
        for card in my_state.hand:
            score = hand_score(card.id, False)
            hand_scores.append(score)
            if score < 0:
                negative_hand_count += 1
            hand_counts[card.id] += 1
            if card_table[card.id].cardType == CardType.SUPPORTER and card.id != Boss_Orders:
                support_count += 1

        no_draw = (my_state.deckCount <= 8)  # Whether to restrict actions that reduce the deck
        do_switch = (not can_main_attack and (bench_attacker or (active_id != Budew and field_counts[Budew] >= 1 and state.turn >= 2)))
        if USE_OPPONENT_ADAPTATION and _opponent_is_crustle_wall(obs, my_index) and active_id == Budew:
            do_switch = True
        effect_card_id = 0 if select.effect == None else select.effect.id
        context_card_id = 0 if select.contextCard == None else select.contextCard.id
    
        scores = []  # Score for each action
        for o in select.option:
            score = 0  # The default and baseline score is 0.
            if o.type == OptionType.NUMBER:
                score = o.number
            elif o.type == OptionType.YES:
                if context == SelectContext.IS_FIRST:
                    score = -1
                else:
                    score = 1
            elif o.type == OptionType.CARD:
                card = get_card(obs, o.area, o.index, o.playerIndex)
                if card != None:
                    energy_count = 0
                    hp = 0
                    if isinstance(card, Pokemon):
                        energy_count = len(card.energies)
                        hp = card.hp
                    if (context == SelectContext.SWITCH
                        or context == SelectContext.TO_ACTIVE
                        or context == SelectContext.SETUP_ACTIVE_POKEMON):
                        # Selection of the Pokémon to send to the Active Spot
                        if o.playerIndex == my_index:
                            if card.id == Dreepy:
                                score += 10000
                            elif card.id == Drakloak:
                                if energy_count >= 1:
                                    score += 20000
                                else:
                                    score -= 10000
                            elif card.id == Dragapult_ex:
                                score += 50000
                            elif card.id == Budew:
                                if context != SelectContext.SWITCH:
                                    score += 100000
                                elif not bench_attacker:
                                    score += 30000
                            elif card.id == Fezandipiti_ex:
                                score -= 1000
                            elif card.id == Meowth_ex:
                                score -= 2000
                        else:
                            if plan_a.attack == o.index + 1:
                                score += 100000
                        score += energy_count * 1000
                        score += hp
                    elif context == SelectContext.SETUP_BENCH_POKEMON:
                        if my_index == state.firstPlayer or card.id != Dreepy:
                            score = -1
                    elif context == SelectContext.TO_BENCH or context == SelectContext.TO_HAND:
                        score = hand_score(card.id, False)
                        hand_counts[card.id] += 1
                        if effect_card_id == Crispin:
                            # Reverse scoring
                            score = 100000 - hand_score(card.id, True)
                    elif context == SelectContext.DISCARD:
                        hand_counts[card.id] -= 1
                        if card_table[card.id].cardType == CardType.SUPPORTER:
                            support_count -= 1
                        score = -hand_score(card.id, False)
                    elif context == SelectContext.DAMAGE_COUNTER or context == SelectContext.DAMAGE_COUNTER_ANY:
                        if hp > 0:
                            score = 100000 - 10 * hp + pokemon_score(card, False)
                            if context == SelectContext.DAMAGE_COUNTER:
                                if 210 <= hp <= 230:
                                    score += 20000 + hp * 20
                                    if o.area == AreaType.ACTIVE:
                                        score += 10000
                                elif 40 <= hp <= 90:
                                    score += 10000 + hp * 20
                                elif hp <= 30:
                                    score += -10000 + hp * 20
                                if card.id == 133 or card.id == 351:
                                    score += 30000
                            else:
                                index = o.index + 1
                                if index in plan_b.counter:
                                    score += 100000
                                else:
                                    remain_damage = select.remainDamageCounter * 10
                                    if 210 <= hp <= 200 + remain_damage:
                                        score += 30000
                                    elif 20 <= hp <= 60 + remain_damage:
                                        score += 10000
                                    elif hp == 10:
                                        score -= 100000
                                if no_damage_counter(card):
                                    score = -1
                    elif context == SelectContext.ATTACH_FROM:
                        score = attach_score(context_card_id, card, o.area == AreaType.ACTIVE)
                        if card.id == Dragapult_ex:
                            score += 200
            elif o.type == OptionType.ENERGY_CARD or o.type == OptionType.ENERGY:
                # Discarding energy (Retreat or Crushing Hammer)
                if o.playerIndex != state.yourIndex:
                    if o.area == AreaType.BENCH:
                        score = 20
                    else:
                        score = 10
                    card = get_card(obs, o.area, o.index, o.playerIndex)
                    if card_table[card.id].cardType == CardType.SPECIAL_ENERGY:
                        score += 1
            elif o.type == OptionType.PLAY:
                card = get_card(obs, AreaType.HAND, o.index, my_index)
                card_score = hand_scores[o.index]
                if card.id == Dreepy:
                    score = 51000
                elif card.id == Fezandipiti_ex:
                    if card_score > 0:
                        score = 53000
                    else:
                        score = -1
                elif card.id == Latias_ex:
                    if active_id != Drakloak and active_id != Dragapult_ex:
                        score = 51000
                    else:
                        score = -1
                elif card.id == Budew:
                    if field_counts[Budew] == 0 and field_counts[Dragapult_ex] == 0:
                        score = 52000
                    else:
                        score = -1
                elif card.id == Meowth_ex:
                    if state.supporterPlayed or stadium_id == Team_Rocket_Watchtower:
                        score = -1
                    elif support_count == 0:
                        score = 50000
                    elif support_count == hand_counts[Boss_Orders] and not plan_a.attack <= 0:
                        score = 50000
                    else:
                        score = -1
                elif card.id == Rare_Candy:
                    if no_more_dex:
                        score = -1
                    else:
                        score = 75000
                elif card.id == Unfair_Stamp:
                    score = 15000
                elif card.id == Night_Stretcher:
                    if card_score >= 18000:
                        score = 42000
                    else:
                        score = -1
                elif card.id == Crushing_Hammer:
                    score = 40000
                elif card.id == Boss_Orders:
                    if card.id == use_support:
                        score = 35000
                    else:
                        score = -1
                elif card.id == Lillie_Determination:
                    if card.id == use_support:
                        score = 14000
                    else:
                        score = -1
                elif card.id == Team_Rocket_Watchtower:
                    if stadium_id > 0 or state.turn == 1:
                        score = 80000
                    else:
                        score = -1
                elif no_draw:
                    score = -1
                elif card.id == Buddy_Buddy_Poffin:
                    if deck_counts[Dreepy] > 0:
                        score = 46000
                    else:
                        score = -1
                elif card.id == Ultra_Ball:
                    if negative_hand_count >= 2:
                        score = 44000
                    else:
                        score = -1
                elif card.id == Poke_Pad:
                    if deck_counts[Dreepy] + deck_counts[Drakloak] > 0:
                        score = 45000
                    else:
                        score = -1
                elif card.id == Crispin or card.id == Brock_Scouting:
                    if card.id == use_support:
                        score = 35000
                    else:
                        score = -1
            elif o.type == OptionType.ATTACH:
                card = get_card(obs, o.area, o.index, my_index)
                pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, my_index)
                score = attach_score(card.id, pokemon, o.inPlayArea == AreaType.ACTIVE)
            elif o.type == OptionType.EVOLVE:
                pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, my_index)
                score += len(pokemon.energies)
                if pokemon.id == Dreepy:
                    score += 30000
                elif field_counts[Dragapult_ex] >= 2 or (field_counts[Dragapult_ex] == 1 and len(op_state.prize) <= 2):
                    score = -1
                else:
                    score += 70000
            elif o.type == OptionType.ABILITY:
                card = get_card(obs, o.area, o.index, my_index)
                if no_draw:
                    score = -1
                elif card.id == 1267:  # Lumiose City
                    score = 1
                else:
                    score = 40000
            elif o.type == OptionType.RETREAT:
                if do_switch:
                    score = 10000
                else:
                    score = -1
            elif o.type == OptionType.ATTACK:
                score = (20000 + o.attackId) if can_main_attack else o.attackId

            scores.append(score)

        output = []
        if len(scores) >= 1:
            # Select in descending order of score
            sorted_scores = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            for i in range(select.maxCount):
                # If the score is negative, do not select it if skipping is possible
                if (sorted_scores[i][1] >= 0
                    or select.minCount > i
                    or (context != SelectContext.TO_BENCH and context != SelectContext.SETUP_BENCH_POKEMON)):
                    output.append(sorted_scores[i][0])
                
        return output


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
    try:
        sbi = _search_begin_hidden(obs)
        nxt = _unwrap_search(sbi)
        if nxt is None:
            return -float("inf")
        ar = search_step(nxt.searchId, [action])
        stepped = _unwrap_search(ar)
        if stepped is None:
            return -float("inf")
        cur = rollout_turn(stepped.searchId, stepped.observation, obs.current.yourIndex)
        return evaluate_state(cur)
    except Exception:
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
