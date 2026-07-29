DECK = [360, 360, 360, 360, 361, 361, 361, 361, 1030, 1030, 1031, 1031, 1031, 140, 1086, 1086, 1086, 1086, 1121, 1121, 1121, 1121, 1079, 1079, 1079, 1182, 1182, 1097, 1097, 1088, 1119, 1119, 1246, 1246, 1227, 1227, 1227, 1227, 1225, 1225, 1123, 1123, 1122, 1122, 11, 11, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

import random

def agent(obs_dict):
    if obs_dict.get("select") is None:
        return DECK
    sel = obs_dict["select"]
    n = len(sel["option"])
    k = sel["maxCount"]
    return random.sample(range(n), k)
