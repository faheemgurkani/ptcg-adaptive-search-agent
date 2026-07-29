"""Extract Phase 1 holdout opponent assets from local reference notebooks."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_NB = ROOT / "docs/resources/reference_notebooks/pok-mon-tcg-ai-battle-meta-snapshot-07-july.ipynb"
HOLDOUT_DIR = ROOT / "notebooks/holdout"
PANEL = HOLDOUT_DIR / "panel"


def _load_meta_ns() -> dict:
    ns: dict = {}
    for cell in json.loads(META_NB.read_text(encoding="utf-8"))["cells"]:
        if cell["cell_type"] == "code" and "AGENT_PAYLOADS" in "".join(cell["source"]):
            exec("".join(cell["source"]), ns)
            break
    return ns


def _write_deck(path: Path, deck: list[int]) -> None:
    path.write_text("\n".join(str(c) for c in deck) + "\n", encoding="utf-8")


def _random_agent_source() -> str:
    return textwrap.dedent(
        '''
        import random

        def agent(obs_dict):
            if obs_dict.get("select") is None:
                return DECK
            sel = obs_dict["select"]
            n = len(sel["option"])
            k = sel["maxCount"]
            return random.sample(range(n), k)
        '''
    ).strip()


def main() -> None:
    ns = _load_meta_ns()
    payloads = ns["AGENT_PAYLOADS"]

    PANEL.mkdir(parents=True, exist_ok=True)

    # Alakazam — full rule-based agent + deck from meta snapshot (payload B).
    alakazam_dir = PANEL / "alakazam"
    alakazam_dir.mkdir(exist_ok=True)
    alakazam_deck = [int(x) for x in payloads["B"]["deck_csv"].strip().splitlines() if x.strip()]
    _write_deck(alakazam_dir / "deck.csv", alakazam_deck)
    (alakazam_dir / "main.py").write_text(payloads["B"]["main_py"], encoding="utf-8")

    # Crustle / Spidops / Starmie — deck placeholders using official sample list until
    # dedicated public lists are added. Random opponent agent (same harness for A vs B).
    sample_deck = [
        int(x)
        for x in (
            ROOT / "data/pokemon-tcg-ai-battle/sample_submission/sample_submission/deck.csv"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if x.strip()
    ]
    for name in ("crustle", "spidops", "starmie"):
        opp_dir = PANEL / name
        opp_dir.mkdir(exist_ok=True)
        _write_deck(opp_dir / "deck.csv", sample_deck)
        deck_literal = ", ".join(str(c) for c in sample_deck)
        (opp_dir / "main.py").write_text(
            f"DECK = [{deck_literal}]\n\n{_random_agent_source()}\n",
            encoding="utf-8",
        )
        (opp_dir / "README.txt").write_text(
            f"{name}: placeholder deck (official sample list). Replace deck.csv when a "
            f"field-accurate {name} list is available.\n",
            encoding="utf-8",
        )

    manifest = {
        "phase": 1,
        "opponents": {
            "alakazam": {
                "deck": str(alakazam_dir / "deck.csv"),
                "agent": str(alakazam_dir / "main.py"),
                "agent_type": "rule_based_meta_snapshot_B",
            },
            "crustle": {
                "deck": str(PANEL / "crustle/deck.csv"),
                "agent": str(PANEL / "crustle/main.py"),
                "agent_type": "random_placeholder_deck",
            },
            "spidops": {
                "deck": str(PANEL / "spidops/deck.csv"),
                "agent": str(PANEL / "spidops/main.py"),
                "agent_type": "random_placeholder_deck",
            },
            "starmie": {
                "deck": str(PANEL / "starmie/deck.csv"),
                "agent": str(PANEL / "starmie/main.py"),
                "agent_type": "random_placeholder_deck",
            },
        },
    }
    (HOLDOUT_DIR / "panel_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote holdout panel under {PANEL}")


if __name__ == "__main__":
    main()
