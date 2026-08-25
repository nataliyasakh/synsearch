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
import re
import streamlit as st
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from groq import Groq

VILLAGE_MAP = {
    "dd27c19e-d5a1-4b9e-9862-5a272dde6f23": "Agriculture",
    "e52aa171-f68b-4ec1-ac31-9a5a9b7975c1": "Art & Design",
    "776c19c2-de7d-4a1e-a0c3-a17708887721": "Biomanufacturing",
    "a770e27b-d43a-48c9-a066-5ea0893eff11": "Bioremediation",
    "78d23758-8754-4fbb-bbf0-e1e56119ab9d": "Climate Crisis",
    "eaf1cc50-8041-4f25-a0c3-d5652a653725": "Community Labs",
    "1228b2cd-fb09-4035-bb1e-1d0d5e099877": "Conservation",
    "c318537d-0abc-4350-ae1b-d5b5a653819d": "Diagnostics",
    "6eedeb0f-7be5-4e60-84a8-6036548ca5fa": "Energy",
    "b3a68c75-0813-499f-ac42-1b8ccfd8ca53": "Entrepreneurship",
    "1e7c3c61-3a04-422f-82e6-d7c1f821cff6": "Environment",
    "fec79e23-8f03-467b-92ed-65a24c02877a": "Fashion & Cosmetics",
    "93f00f64-98fe-4aa7-ad4b-13407f7ba52f": "Food & Energy",
    "1967ad47-c93d-483c-b893-867d3070745f": "Food & Nutrition",
    "b62883b7-b186-465c-a381-f9dce17ddbcf": "Foundational Advance",
    "e36904ef-6c13-4442-9286-210a92e84e6e": "Hardware",
    "cedc951d-d1f3-4821-854d-1cd3e5b69f58": "Health & Medicine",
    "41007480-b7f7-4280-a995-8dee381ee316": "High School",
    "bb208fb6-063b-40ec-af0a-9a324c26f43a": "Infectious Diseases",
    "989c935a-4656-495d-8b27-123edd8d1969": "Information Processing",
    "b3b30a28-16d2-454e-8ed2-cb405efc58b0": "Manufacturing",
    "9d79569b-499f-4c62-847d-9d4176565742": "Measurement",
    "07f2335f-6d0c-4bcb-a8f7-66cba7a4c1df": "Microfluidics",
    "74dee1c1-55d0-44eb-b8b7-6b55f6bd284b": "New Application",
    "d60d87c8-5303-459a-a5a2-79a33e0112be": "Oncology",
    "6b517fe0-b9fd-4b55-be50-926665198b13": "Open",
    "e698aebf-a08f-464a-8cb6-0a3764d698f1": "Policy & Practices",
    "2c6416dd-b087-40ed-ace0-2b4c12cd5700": "Software",
    "ccc0d43f-6a7e-4838-a751-afb408ae17fb": "Software & AI",
    "f18865a1-65a6-4112-9ad0-485fa50be8f8": "Space",
    "8cca60cf-f3b9-4f2a-aca3-b2c426461f88": "Therapeutics"
}


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
    if year not in ("All years", "All years (2019 corpus)", ""):
        try:
            f["year"] = {"$eq": int(year)}
        except ValueError:
            pass
    if track not in ("All tracks", "All villages", ""):
        f["track"] = {"$eq": track}
    if medal not in ("Any medal", ""):
        f["prize"] = {"$eq": medal}
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
            raw_track = m.get("track", "")
            raw_medal = m.get("prize", m.get("medal", ""))
            sources.append({
                "num":   i,
                "team":  m.get("team",""),
                "year":  m.get("year",""),
                "track": VILLAGE_MAP.get(raw_track, raw_track) if raw_track else "",
                "medal": raw_medal if raw_medal and raw_medal not in ("Unknown", "-", "") else "",
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

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', raw)
    raw = re.sub(r'\*(.+?)\*', r'<em>\1</em>', raw)
    answer_html = raw

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
        raw_track2 = m.get("track", "")
        raw_medal2 = m.get("prize", m.get("medal", ""))
        similar.append({
            "score": int(match.score * 100),
            "team":  m.get("team", ""),
            "year":  m.get("year", ""),
            "title": m.get("title", m.get("page", "")),
            "track": VILLAGE_MAP.get(raw_track2, raw_track2) if raw_track2 else "",
            "medal": raw_medal2 if raw_medal2 and raw_medal2 not in ("Unknown", "-", "") else "",
            "url":   m.get("url", ""),
        })
        if len(similar) == k:
            break

    return similar
