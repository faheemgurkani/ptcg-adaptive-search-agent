DECK = [37, 37, 37, 37, 344, 344, 344, 344, 345, 345, 345, 345, 1121, 1121, 1121, 1121, 1227, 1227, 1227, 1227, 1197, 1159, 1147, 1192, 1192, 1122, 1122, 1122, 1122, 1182, 1182, 1182, 1182, 1097, 1097, 1097, 1097, 1198, 1198, 1198, 1198, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 11, 18, 1081, 1081, 1094, 1094, 1094]

import random

def agent(obs_dict):
    if obs_dict.get("select") is None:
        return DECK
    sel = obs_dict["select"]
    n = len(sel["option"])
    k = sel["maxCount"]
    return random.sample(range(n), k)
