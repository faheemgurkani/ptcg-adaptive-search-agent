#!/usr/bin/env python3
"""Phase 5 adaptation analysis from Phase 3 V1/V3 + panel deck overlap.

Does not rerun holdout. Per-decision detector traces are not in Phase 3 logs.
Empty-board false positives are answered from the detector definition.
"""

from __future__ import annotations

import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
PHASE3_JSON = REPO / "docs/phases/phase_03/PHASE_03_RESULTS.json"
PHASE5 = REPO / "docs/phases/phase_05"
PANEL = REPO / "notebooks/holdout/panel"

OPP_WATER = {721, 722, 723, 360, 361, 1030, 1031}
OPP_CRUSTLE = {344, 345}
OPP_ORDER = ("alakazam", "crustle", "spidops", "starmie")

WATER_LABELS = {
    721: "Wugtrio line",
    722: "Wugtrio line",
    723: "Wugtrio line",
    360: "Starmie line",
    361: "Starmie line",
    1030: "Mega Starmie",
    1031: "Mega Starmie",
}
CRUSTLE_LABELS = {344: "Dwebble", 345: "Crustle"}


def load_deck_ids(name: str) -> set[int]:
    path = PANEL / name / "deck.csv"
    ids: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(int(line))
    return ids


def main() -> None:
    phase3 = json.loads(PHASE3_JSON.read_text(encoding="utf-8"))
    overlap: dict[str, dict] = {}
    for opp in OPP_ORDER:
        ids = load_deck_ids(opp)
        overlap[opp] = {
            "water_ids": sorted(ids & OPP_WATER),
            "crustle_ids": sorted(ids & OPP_CRUSTLE),
            "water_hit": bool(ids & OPP_WATER),
            "crustle_hit": bool(ids & OPP_CRUSTLE),
        }

    v1 = phase3["matchups"]["v1"]
    v3 = phase3["matchups"]["v3"]
    deltas = {
        opp: round((v3[opp]["win_rate"] - v1[opp]["win_rate"]) * 100, 1)
        for opp in OPP_ORDER
    }

    payload = {
        "phase": 5,
        "status": "offline_complete_traces_deferred",
        "source": "Phase 3 V1 vs V3 (panel v2, repaired choose()); static detector audit",
        "detectors": {
            "water": {
                "ids": sorted(OPP_WATER),
                "labels": WATER_LABELS,
                "signal": "visible opponent active+bench IDs only",
                "hook": "+8000 energy-attach score on Dragapult-ex",
                "empty_board": False,
            },
            "crustle": {
                "ids": sorted(OPP_CRUSTLE),
                "labels": CRUSTLE_LABELS,
                "signal": "visible opponent active+bench IDs only",
                "hook": "force switch off Budew",
                "empty_board": False,
            },
        },
        "panel_overlap": overlap,
        "false_positive": {
            "empty_board_can_fire": False,
            "reason": "_opponent_has requires a matching ID in active+bench; empty board returns False (false negative until the ID appears, not a false positive).",
            "cross_deck_list_overlap": {
                opp: overlap[opp]["water_hit"] or overlap[opp]["crustle_hit"]
                for opp in OPP_ORDER
            },
            "note": "List overlap is intended on Crustle (crustle IDs) and Starmie (water IDs). Alakazam and Spidops lists share neither set.",
        },
        "v1_vs_v3": {
            opp: {
                "v1": v1[opp]["win_rate"],
                "v3": v3[opp]["win_rate"],
                "v1_record": f"{v1[opp]['wins']}/{v1[opp]['games']}",
                "v3_record": f"{v3[opp]['wins']}/{v3[opp]['games']}",
                "delta_pp": deltas[opp],
            }
            for opp in OPP_ORDER
        },
        "pooled": {
            "v1": phase3["pooled"]["v1"]["equal_weight_pool"],
            "v3": phase3["pooled"]["v3"]["equal_weight_pool"],
            "delta_pp": round(
                (phase3["pooled"]["v3"]["equal_weight_pool"] - phase3["pooled"]["v1"]["equal_weight_pool"])
                * 100,
                1,
            ),
        },
        "decisions": [
            "Do not add a Spidops or Festival detector. Adaptation already fails its primary Crustle hypothesis (−15.0 pp). Spidops V3 is 40/40 without a dedicated hook.",
            "Do not change Crustle/water weights. Measuring the current hooks is the Phase 5 goal; retuning would mix attribution with a new policy.",
            "Per-decision fire-time traces need an instrumented V3 rerun; Phase 3 CSVs have outcomes only. Deferred.",
        ],
        "findings": [
            "Adaptive weights matter: they reduce win rate (V3−V1 = −5.0 pp pooled; Crustle −15.0 pp).",
            "Empty-board early game cannot false-positive: detectors require a visible matching ID.",
            "Panel lists have zero unintended ID overlap (Alakazam/Spidops share neither water nor Crustle IDs).",
            "Water hook is the intended Starmie true-positive (360/361/1030/1031 in the Starmie list) and still −2.5 pp vs V1.",
            "No extra archetype detector this cycle.",
        ],
        "verdict": "Opponent adaptation as implemented hurts vs the static policy. Keep adaptation off (V1). Do not expand detectors.",
    }

    PHASE5.mkdir(parents=True, exist_ok=True)
    (PHASE5 / "offline").mkdir(exist_ok=True)
    out = PHASE5 / "PHASE_05_RESULTS.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("wrote", out)
    print("pooled V3-V1", payload["pooled"]["delta_pp"], "pp")
    print("crustle", deltas["crustle"], "pp")
    for opp, row in overlap.items():
        print(opp, "water", row["water_ids"], "crustle", row["crustle_ids"])


if __name__ == "__main__":
    main()
