DECK = [1158, 721, 721, 722, 722, 722, 722, 723, 723, 723, 723, 1145, 1145, 1145, 1145, 1205, 1205, 1227, 1227, 1227, 1227, 1235, 1235, 1235, 1235, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

import random

def agent(obs_dict):
    if obs_dict.get("select") is None:
        return DECK
    sel = obs_dict["select"]
    n = len(sel["option"])
    k = sel["maxCount"]
    return random.sample(range(n), k)
