# cabt Engine — Local Documentation

Offline documentation for the **PTCGABC cabt Engine** (Matsuo Institute), used by the Kaggle PTCG AI Battle competition.

Online source: https://matsuoinstitute.github.io/cabt/

**Runtime status:** With macOS quarantine cleared, `cg` imports work locally (`1267` cards via `all_card_data()`). Use `.venv` for all commands.

---

## Where to look (AI agents)

| Task | Path |
|------|------|
| **Entry point / routing table** | [`docs/resources/cabt/LOCAL_README.md`](resources/cabt/LOCAL_README.md) |
| **Overview + Getting Started** | [`docs/resources/cabt/html/index.html`](resources/cabt/html/index.html) |
| **Full API reference (official HTML)** | [`docs/resources/cabt/html/api.html`](resources/cabt/html/api.html) |
| **API from your installed SDK (pdoc)** | [`docs/resources/cabt/pdoc/index.html`](resources/cabt/pdoc/index.html) |
| **Game module** | [`docs/resources/cabt/html/game.html`](resources/cabt/html/game.html) |
| **Python source snapshot** | [`docs/resources/cabt/sdk/`](resources/cabt/sdk/) |
| **Markdown API summaries** | [`docs/resources/cabt/api_markdown/`](resources/cabt/api_markdown/) |
| **Runtime SDK (execute code)** | `data/pokemon-tcg-ai-battle/sample_submission/sample_submission/cg/` |

`docs/resources/` is gitignored — content exists on your machine after refresh; this file is the tracked map.

**Do not use Context7 for cabt API** — it is not indexed. Use paths above or `help()` on live imports.

---

## Structure

```
docs/resources/cabt/
├── LOCAL_README.md       # detailed routing (start here when browsing locally)
├── html/                 # mirrored official Sphinx site
├── pdoc/                 # HTML generated from local cg/*.py (matches your binaries)
├── sources/              # RST sources + objects.inv
├── sdk/                  # cg/*.py snapshot
├── api_markdown/         # Markdown API extracts
└── scripts/
    ├── refresh_cabt_docs.sh
    ├── verify_cabt_runtime.sh
    └── build_api_markdown.py
```

---

## Verify runtime (`.venv`)

```bash
source .venv/bin/activate
bash docs/resources/cabt/scripts/verify_cabt_runtime.sh
```

Quick API help:

```bash
python -c "
import sys
sys.path.insert(0, 'data/pokemon-tcg-ai-battle/sample_submission/sample_submission')
from cg import api, game
help(game.battle_start)
help(api.search_begin)
"
```

---

## Refresh offline docs

```bash
bash docs/resources/cabt/scripts/refresh_cabt_docs.sh
```

Re-downloads the Sphinx mirror, refreshes `sdk/`, `api_markdown/`, and `pdoc/`.

---

## macOS quarantine (one-time)

If `cg` import fails with `library load disallowed by system policy`:

```bash
xattr -dr com.apple.quarantine data/pokemon-tcg-ai-battle/sample_submission/sample_submission/cg
```

---

## kaggle-environments

Installed via `requirements.txt`. Official Getting Started pattern:

```python
from kaggle_environments import make
env = make("cabt", configuration={"decks": [deck, deck]})
env.run([agent, agent])
```

For Phase 1 holdout work, prefer `cg.game.battle_start` directly (same engine, lower level).
