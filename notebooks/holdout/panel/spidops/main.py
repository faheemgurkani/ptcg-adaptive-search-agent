DECK = [400, 400, 400, 400, 401, 401, 401, 140, 1086, 1086, 1086, 1086, 1121, 1121, 1121, 1121, 1079, 1079, 1182, 1182, 1097, 1097, 1081, 1081, 1227, 1227, 1227, 1227, 1225, 1225, 1122, 1122, 1123, 1123, 1246, 1246, 1152, 1152, 1088, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

import random

def agent(obs_dict):
    if obs_dict.get("select") is None:
        return DECK
    sel = obs_dict["select"]
    n = len(sel["option"])
    k = sel["maxCount"]
    return random.sample(range(n), k)
