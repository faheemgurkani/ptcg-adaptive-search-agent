"""Meta-snapshot field helpers (Docs 9/11) for Phase 2 deck selection."""

from __future__ import annotations

import json
import re
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
META_NB = ROOT / "docs/resources/reference_notebooks/pok-mon-tcg-ai-battle-meta-snapshot-07-july.ipynb"

# Map holdout panel names → meta snapshot archetype keys (usage/score).
PANEL_TO_META = {
    "alakazam": "alakazam_dunsparce",
    "crustle": None,  # not a top meta row; excluded from usage-weighted edge
    "spidops": "team_rocket_spidops",
    "starmie": "starmie",
}


def _unescape_py_json_string(raw: str) -> str:
    return bytes(raw, "utf-8").decode("unicode_escape")


def load_snapshot_bundle(nb_path: Path = META_NB) -> dict[str, Any]:
    src = "".join(json.loads(nb_path.read_text(encoding="utf-8"))["cells"][1]["source"])
    start = src.find("json.loads('")
    if start < 0:
        raise RuntimeError(f"No snapshot json.loads in {nb_path}")
    i = start + len("json.loads('")
    buf: list[str] = []
    j = i
    while j < len(src):
        ch = src[j]
        if ch == "\\":
            buf.append(src[j : j + 2])
            j += 2
            continue
        if ch == "'":
            break
        buf.append(ch)
        j += 1
    return json.loads(_unescape_py_json_string("".join(buf)))


def load_field_chart(nb_path: Path = META_NB) -> pd.DataFrame:
    snap = load_snapshot_bundle(nb_path)
    return pd.read_csv(StringIO(snap["field_chart_csv"]))


def load_ev_chart(nb_path: Path = META_NB) -> pd.DataFrame:
    snap = load_snapshot_bundle(nb_path)
    return pd.read_csv(StringIO(snap["ev_chart_csv"]))


def field_lookup(field_df: pd.DataFrame) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for _, row in field_df.iterrows():
        out[str(row["archetype"])] = {
            "usage_share": float(row["usage_share"]),
            "score_rate": float(row["score_rate"]),
            "games": float(row["games"]),
        }
    return out


def weighted_matchup_metrics(
    matchup_winrates: dict[str, float],
    field: dict[str, dict[str, float]],
    *,
    panel_to_meta: dict[str, str | None] = PANEL_TO_META,
) -> dict[str, Any]:
    """Field-weighted score and edge using meta usage shares.

    weighted_score = Σ u_i * W_i / Σ u_i   (over panel rows with a meta mapping)
    weighted_edge  = weighted_score - Σ u_i * s_i / Σ u_i
      where s_i is the archetype's live score_rate (usage vs conversion mindset)
    """
    num = 0.0
    den = 0.0
    field_num = 0.0
    used: list[dict[str, Any]] = []
    skipped: list[str] = []

    for panel_name, wr in matchup_winrates.items():
        meta_key = panel_to_meta.get(panel_name)
        if meta_key is None or meta_key not in field:
            skipped.append(panel_name)
            continue
        u = field[meta_key]["usage_share"]
        s = field[meta_key]["score_rate"]
        num += u * wr
        field_num += u * s
        den += u
        used.append(
            {
                "panel": panel_name,
                "meta_archetype": meta_key,
                "usage_share": u,
                "field_score_rate": s,
                "our_win_rate": wr,
                "matchup_edge_vs_field_score": wr - s,
            }
        )

    if den <= 0:
        return {
            "weighted_score_rate": None,
            "weighted_field_score_rate": None,
            "weighted_edge_vs_field": None,
            "covered_field_weight": 0.0,
            "matchups_used": used,
            "matchups_skipped": skipped,
        }

    w_score = num / den
    w_field = field_num / den
    return {
        "weighted_score_rate": w_score,
        "weighted_field_score_rate": w_field,
        "weighted_edge_vs_field": w_score - w_field,
        "covered_field_weight": den,
        "matchups_used": used,
        "matchups_skipped": skipped,
    }


def equal_weight_overall(matchup_winrates: dict[str, float]) -> float:
    if not matchup_winrates:
        return 0.0
    return sum(matchup_winrates.values()) / len(matchup_winrates)
