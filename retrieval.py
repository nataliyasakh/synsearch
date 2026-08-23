"""
retrieval.py — the real RAG backend for SynSearch.

Two public functions used by app.py:
  search(query, year, track, medal, k=5)
    → (answer_html, sources, similar)

  find_similar(query, k=4)
    → similar list (used on the Similar Projects page)

Keys are read from Streamlit secrets when running on Streamlit Cloud,
or from environment variables when running locally.
"""

import os
import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from groq import Groq

# ── Load clients (cached so they only initialise once per session) ────────────

@st.cache_resource
def _load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def _load_pinecone():
    key = st.secrets.get("PINECONE_API_KEY") or os.environ.get("PINECONE_API_KEY")
    pc  = Pinecone(api_key=key)
    return pc.Index("synsearch")

@st.cache_resource
def _load_groq():
    key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    return Groq(api_key=key)


# ── Metadata filter builder ───────────────────────────────────────────────────

def _build_filter(year: str, track: str, medal: str) -> dict | None:
    """Convert dropdown selections into a Pinecone metadata filter."""
    f = {}
    if year  != "All years":   f["year"]  = {"$eq": int(year)}
    if track != "All tracks":  f["track"] = {"$eq": track}
    if medal != "Any medal":   f["prize"] = {"$eq": medal}
    return f if f else None


# ── Core search ───────────────────────────────────────────────────────────────

def search(query: str, year="All years", track="All tracks",
           medal="Any medal", k: int = 5):
    """
    Embed the query, retrieve top-k chunks from Pinecone,
    call Groq to synthesise an answer, return (answer_html, sources, similar).
    """
    embedder = _load_embedder()
    index    = _load_pinecone()
    groq     = _load_groq()

    # 1. Embed query
    q_vec = embedder.encode([query], normalize_embeddings=True)[0].tolist()

    # 2. Retrieve from Pinecone (with optional metadata filter)
    results = index.query(
        vector=q_vec,
        top_k=k,
        include_metadata=True,
        filter=_build_filter(year, track, medal),
    )

    if not results.matches:
        return (
            "No results found for that query and filter combination. "
            "Try broadening the year, track, or medal filter.",
            [], []
        )

    # 3. Build context for the LLM
    chunks = []
    sources = []
    seen_teams = set()

    for i, match in enumerate(results.matches, 1):
        m = match.metadata
        chunks.append(f"[{i}] {m['team']} ({m.get('year','')}) — {m.get('title', m.get('page',''))}\n{match.metadata.get('text', '')[:600]}")
        if m["team"] not in seen_teams:
            seen_teams.add(m["team"])
            sources.append({
                "num":   i,
                "team":  m.get("team",""),
                "year":  m.get("year",""),
                "track": m.get("track",""),
                "medal": m.get("prize", m.get("medal","Unknown")),
                "url":   m.get("url",""),
            })

    context = "\n\n---\n\n".join(chunks)

    # 4. Generate answer with Groq
    system_prompt = (
        "You are a synthetic biology research assistant helping iGEM teams "
        "learn from past projects. Answer the user's question using ONLY the "
        "provided source excerpts. After each claim, add an inline citation "
        "like <span class='cite-tag'>[1]</span> matching the source number. "
        "Be concise (3-5 sentences). Never invent information not in the sources."
    )

    user_prompt = (
        f"Question: {query}\n\n"
        f"Sources:\n{context}\n\n"
        "Answer with inline citations:"
    )

    response = groq.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.1,   # low temp = stick to sources
        max_tokens=800,
    )

    answer_html = response.choices[0].message.content.strip()

    # 5. Find similar projects (separate query for the similar panel)
    similar = find_similar(query, k=4)

    return answer_html, sources, similar


# ── Similar projects ──────────────────────────────────────────────────────────

def find_similar(query: str, k: int = 4):
    """
    Return the k most semantically similar iGEM projects to the query.
    Deduplicates by team so you don't get 4 chunks from the same project.
    """
    embedder = _load_embedder()
    index    = _load_pinecone()

    q_vec = embedder.encode([query], normalize_embeddings=True)[0].tolist()

    # Fetch more than k to allow dedup
    results = index.query(vector=q_vec, top_k=k * 3, include_metadata=True)

    seen   = set()
    similar = []
    for match in results.matches:
        m = match.metadata
        if m["team"] in seen:
            continue
        seen.add(m["team"])
        similar.append({
            "score": int(match.score * 100),
            "team":  m.get("team", ""),
            "year":  m.get("year", ""),
            "title": m.get("title", m.get("page", "")),
            "track": m.get("track", ""),
            "medal": m.get("prize", m.get("medal", "Unknown")),
            "url":   m.get("url", ""),
        })
        if len(similar) == k:
            break

    return similar
