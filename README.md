# SynSearch

**iGEM 2026 Software Track** — Open-source RAG system for searching the iGEM knowledge archive.

A wet-lab biologist types a plain-English question. SynSearch retrieves the most relevant past iGEM team wikis and returns a sourced answer with direct links to the original pages. No hallucinated citations. No terminal required.

→ **Live demo:** TODO — replace with your real Streamlit Cloud URL before presenting.

---

## What's in this repo

```
app.py                  # Main Streamlit app (all pages) — runs on demo data out of the box
requirements.txt        # Python dependencies
tools_page.py            # Tools page (not yet in repo — app shows a placeholder until this is added)
harvest_corpus.py        # Converts Munich's xlsx -> corpus.json (not yet in repo)
build_index.py           # Chunks + embeds corpus.json -> Pinecone index (not yet in repo)
retrieval.py             # search() + find_similar() functions (not yet in repo)
.streamlit/config.toml   # Dark theme config (not yet in repo)
```

**Current status:** The UI runs fully on demo data by default. `app.py` automatically falls back to
placeholder answers, sources, and similar-project cards whenever `retrieval.py` or `tools_page.py`
aren't present, so cloning and running this repo today works without crashing. Once you add
`retrieval.py`, `app.py` picks it up automatically — no manual code changes needed.

---

## Run locally

```
pip install -r requirements.txt
streamlit run app.py
```

No API key needed for the demo. The full pipeline (once `retrieval.py` is built) additionally needs:

```
pip install requests beautifulsoup4
```

...plus a `PINECONE_API_KEY` and `GROQ_API_KEY` set as environment variables.

---

## Building the real index

1. Download `processed_data.xlsx` from the Munich 2024 repo (see Attribution below)
2. Run `python harvest_corpus.py` → produces `corpus.json`
3. Run `python build_index.py` → embeds and upserts vectors into your Pinecone index
4. Add `retrieval.py` with `search()` and `find_similar()` functions matching the signatures called
   in `app.py` — the demo fallback disappears automatically once the file exists

---

## What we built vs. what we inherited

**Inherited (Munich 2024, CC BY 4.0):**

- Pre-scraped 2019 iGEM wiki corpus (343 teams, `processed_data.xlsx`)
- Original scraper logic (`process_data.py`)

**Built by us:**

- Inline source citations with direct wiki links (Munich listed this as future work)
- Metadata filtering by year, track, and medal before retrieval
- "Similar projects" semantic explorer — not available anywhere else
- Three-way RAGAS benchmark: bare Groq model vs. Groq (fast) + RAG vs. Groq (large) + RAG
- Zero-install hosted interface — no Docker, no user API key required for the demo
- Lighter stack: sentence-transformers + Pinecone replaces Docker + Qdrant

---

## Attribution

The 2019 iGEM wiki corpus used in this project was scraped and curated by the **Munich 2024 iGEM team** and is used under Creative Commons Attribution 4.0
International (CC BY 4.0).

Source: <https://gitlab.igem.org/2024/software-tools/munich>

---

## Benchmark

| System                       | Faithfulness | Answer Relevancy | Context Recall |
| ----------------------------- | ------------ | ----------------- | --------------- |
| Bare Groq (no retrieval)      | 0.11         | 0.75              | 0.12            |
| Groq (fast) + SynSearch RAG   | 0.42         | 0.19              | 0.30            |
| Groq (large) + SynSearch RAG  | 0.79         | 0.27              | 0.21            |

Evaluated on 50 manually-verified iGEM-specific questions using RAGAS. These are the same demo
numbers shown on the app's Benchmark page — update both together once a full evaluation run is
complete. **Worth double-checking before presenting:** answer relevancy and context recall both
drop from the bare model to the RAG variants, and the "large" RAG model scores lower on context
recall than the "fast" one — that pattern is unusual for a retrieval system and may indicate the
demo numbers were placeholders rather than a real run.

---

## License

MIT. The Munich 2024 corpus retains its original CC BY 4.0 licence.
