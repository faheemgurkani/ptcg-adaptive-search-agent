# cabt Engine — Local Documentation

Offline documentation for the **PTCGABC cabt Engine** (Matsuo Institute), used by the Kaggle PTCG AI Battle competition.

Online source: https://matsuoinstitute.github.io/cabt/

---

## Where to look (AI agents)

| Task | Path |
|------|------|
| **Entry point / routing table** | [`docs/resources/cabt/LOCAL_README.md`](resources/cabt/LOCAL_README.md) |
| **Overview + Getting Started** | [`docs/resources/cabt/html/index.html`](resources/cabt/html/index.html) |
| **Full API reference (HTML)** | [`docs/resources/cabt/html/api.html`](resources/cabt/html/api.html) |
| **Game module** | [`docs/resources/cabt/html/game.html`](resources/cabt/html/game.html) |
| **Python source snapshot** | [`docs/resources/cabt/sdk/`](resources/cabt/sdk/) |
| **Markdown API summaries** | [`docs/resources/cabt/api_markdown/`](resources/cabt/api_markdown/) |
| **Runtime SDK (execute code)** | `data/pokemon-tcg-ai-battle/sample_submission/sample_submission/cg/` |

`docs/resources/` is gitignored — content exists on your machine after refresh; this file is the tracked map.

---

## Structure

```
docs/resources/cabt/
├── LOCAL_README.md       # detailed routing (start here when browsing locally)
├── html/                 # mirrored Sphinx site
├── sources/              # RST sources + objects.inv
├── sdk/                  # cg/*.py snapshot
├── api_markdown/         # Markdown API extracts
└── scripts/
    └── refresh_cabt_docs.sh
```

---

## Refresh offline docs

Uses project `.venv`:

```bash
bash docs/resources/cabt/scripts/refresh_cabt_docs.sh
```

---

## Context7

Context7 does **not** index cabt. Use this local mirror and `docs/resources/cabt/sdk/` instead.
