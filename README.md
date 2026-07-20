# SynSearch

**iGEM 2025 Software Track** — Open-source RAG system for searching the iGEM knowledge archive.

A wet-lab biologist types a plain-English question. SynSearch retrieves the most relevant past iGEM team wikis and returns a sourced answer with direct links to the original pages. No hallucinated citations. No terminal required.

→ **[Live demo](https://your-app.streamlit.app)** (replace with your Streamlit Cloud URL)

---

## What's in this repo

```
app.py                  # Main Streamlit app (all pages)
requirements.txt        # Python dependencies
.streamlit/config.toml  # Dark theme config
harvest_corpus.py       # Converts Munich's xlsx → corpus.json (run once)
build_index.py          # Chunks + embeds corpus.json → Chroma index (run once, add later)
retrieval.py            # Search + similar-projects functions (add later)
```

**Current status:** The UI runs fully on demo data. Swap the `DEMO_*` constants
in `app.py` for real calls to `retrieval.py` once the Chroma index is built.

---

## Run locally

```bash
pip install streamlit
streamlit run app.py
```

No API key needed for the demo. The full pipeline additionally requires:

```bash
pip install sentence-transformers chromadb pandas requests beautifulsoup4
```

---

## Building the real index

1. Download `processed_data.xlsx` from the Munich 2024 repo (see Attribution below)
2. Run `python harvest_corpus.py` → produces `corpus.json`
3. Run `python build_index.py` → produces a local Chroma vector store
4. Uncomment the import in `app.py` and remove the demo data block

---

## What we built vs. what we inherited

**Inherited (Munich 2024, CC BY 4.0):**
- Pre-scraped 2019 iGEM wiki corpus (343 teams, `processed_data.xlsx`)
- Original scraper logic (`process_data.py`)

**Built by us:**
- Inline source citations with direct wiki links (Munich listed this as future work)
- Metadata filtering by year, track, and medal before retrieval
- "Similar projects" semantic explorer — not available anywhere else
- Three-way RAGAS benchmark: bare GPT-4o vs GPT-4o+RAG vs open model+RAG
- Zero-install hosted interface — no Docker, no user API key required
- Lighter stack: sentence-transformers + Chroma replaces Docker + Qdrant + Groq

---

## Attribution

The 2019 iGEM wiki corpus used in this project was scraped and curated by the
**Munich 2024 iGEM team** and is used under Creative Commons Attribution 4.0
International (CC BY 4.0).

Source: https://gitlab.igem.org/2024/software-tools/munich

---

## Benchmark

| System | Faithfulness | Answer Relevancy | Context Recall |
|--------|-------------|-----------------|----------------|
| Bare GPT-4o | 0.41 | 0.58 | 0.29 |
| GPT-4o + SynSearch RAG | 0.79 | 0.83 | 0.71 |
| Open model + SynSearch RAG | 0.74 | 0.77 | 0.68 |

Evaluated on 50 manually-verified iGEM-specific questions using RAGAS.
*(placeholder — replace with real numbers when evaluation is run)*

---

## License

MIT. The Munich 2024 corpus retains its original CC BY 4.0 licence.
