# SynSearch

**iGEM 2025 Software & AI Village — NYUAD**

Open-source RAG (retrieval-augmented generation) system for searching the iGEM competition knowledge archive. A wet-lab biologist types a plain-English question and gets sourced answers with direct links to the original team wikis.

→ **[synsearchnyuad.streamlit.app](https://synsearchnyuad.streamlit.app)**

---

## What it does

- **Search** — ask any question in plain English, get a synthesised answer with inline citations linking to specific wiki pages
- **Similar Projects** — describe your project and find the most semantically similar past iGEM teams (vector similarity, not keyword matching)
- **Tools** — 59 verified wet-lab software tools with AI recommendations and wiki context showing how iGEM teams actually used each tool
- **Benchmark** — three-way comparison showing RAG improves faithfulness 7× over a bare LLM

---

## Corpus

| Year | Source | Vectors |
|------|--------|---------|
| 2016 | Wayback Machine | 1,333 |
| 2017 | Wayback Machine | 1,338 |
| 2018 | Wayback Machine | 2,392 |
| 2019 | Munich 2024 corpus (CC BY 4.0) | 3,169 |
| 2022 | igem.wiki via iGEM API | 10,505 |
| 2023 | igem.wiki via iGEM API | 12,408 |
| 2024 | igem.wiki via iGEM API | 12,806 |
| 2025 | igem.wiki via iGEM API | 14,677 |
| **Total** | | **58,569** |

---

## Stack

```
sentence-transformers (all-MiniLM-L6-v2)  →  Pinecone  →  Groq (compound-mini)  →  Streamlit Cloud
```

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requires a `.streamlit/secrets.toml` with:
```toml
PINECONE_API_KEY = "..."
GROQ_API_KEY = "..."
```

---

## Rebuild the corpus index

```bash
# Scrape 2022+ wikis via iGEM API
python scrape_corpus.py --year 2022 --delay 1

# Scrape pre-2022 via Wayback Machine
python scrape_wayback.py --year 2018 --delay 2

# Embed and upload to Pinecone
python embed_corpus.py --year 2022
```

---

## Benchmark

Evaluated on 50 manually verified iGEM-specific questions using an LLM-as-judge approach following the RAGAS framework (Es et al., 2023).

| System | Faithfulness | Answer Relevancy | Context Recall |
|--------|-------------|-----------------|----------------|
| Bare Groq (no retrieval) | 0.11 | 0.75 | 0.12 |
| Groq fast + SynSearch RAG | 0.42 | 0.19 | 0.30 |
| Groq large + SynSearch RAG | **0.79** | 0.27 | 0.21 |

RAG improves faithfulness **7×** over a bare LLM on iGEM-specific questions.

---

## What we built vs. what we inherited

**Inherited (Munich 2024, CC BY 4.0):**
- Pre-scraped 2019 iGEM wiki corpus (343 teams)
- Proof of concept that RAG reduces hallucination on iGEM data

**Built by us:**
- Corpus expansion: 343 teams (2019) → 1,000+ teams (2016–2025)
- Scrapers for Wayback Machine (pre-2022) and igem.wiki API (2022+)
- Inline source citations linking to the specific wiki page
- Village/year/medal metadata filtering before retrieval
- Similar Projects semantic explorer
- Tools page with 59 verified tools + AI recommendations + wiki context
- Published three-way benchmark with manually verified ground truth
- Zero-install hosted interface — no Docker, no terminal, no API key required

---

## Attribution

The 2019 iGEM wiki corpus was scraped and curated by the **Munich 2024 iGEM team** and is used under Creative Commons Attribution 4.0 International (CC BY 4.0).

Source: https://gitlab.igem.org/2024/software-tools/munich

**Citation:**
Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. *arXiv:2309.15217*.

---

## License

MIT. The Munich 2024 corpus retains its original CC BY 4.0 licence.
