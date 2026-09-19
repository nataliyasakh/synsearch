"""
registry_search.py — iGEM Parts Registry integration for SynSearch.

Uses the new iGEM Registry REST API (api.registry.igem.org).
No authentication required for public parts.

Usage:
    from registry_search import search_parts
    parts = search_parts("constitutive promoter E. coli", max_results=5)
"""

import requests
import streamlit as st

REGISTRY_BASE = "https://api.registry.igem.org/v1"
HEADERS = {"Accept": "application/json", "User-Agent": "SynSearch-NYUAD-2026"}

# Role label → human readable
ROLE_LABELS = {
    "Promoter":    "Promoter",
    "RBS":         "RBS",
    "CDS":         "Coding Sequence",
    "Terminator":  "Terminator",
    "Composite":   "Composite Part",
    "Generator":   "Generator",
    "Reporter":    "Reporter",
    "Inverter":    "Inverter",
    "Measurement": "Measurement",
    "Cell":        "Cell",
    "Plasmid":     "Plasmid",
}

@st.cache_data(ttl=3600)
def search_parts(query: str, max_results: int = 5) -> list:
    """
    Search the iGEM Parts Registry for parts matching the query.
    Returns a list of dicts with name, title, role, description, url.
    Cached for 1 hour to avoid hammering the API.
    """
    if not query or not query.strip():
        return []
    try:
        r = requests.get(
            f"{REGISTRY_BASE}/parts",
            params={"search": query},
            headers=HEADERS,
            timeout=10
        )
        if r.status_code != 200:
            return []
        data = r.json()
        if "data" not in data:
            return []

        results = []
        for part in data["data"][:max_results]:
            name  = part.get("name", "")
            title = part.get("title", "")
            desc  = part.get("description", "")
            role  = part.get("role", {})
            role_label = role.get("label", "") if role else ""

            # Build URL to the part page
            slug = part.get("slug", "")
            url  = f"https://registry.igem.org/parts/{slug}" if slug else f"https://parts.igem.org/{name}"

            # Truncate description
            short_desc = desc[:200] + "..." if len(desc) > 200 else desc

            results.append({
                "name":        name,
                "title":       title,
                "role":        ROLE_LABELS.get(role_label, role_label),
                "description": short_desc,
                "url":         url,
                "status":      part.get("status", ""),
            })
        return results
    except Exception:
        return []


def render_parts_section(parts: list) -> str:
    """Render a list of parts as HTML for the answer card."""
    if not parts:
        return ""

    html = "<div class='sources-head'>Related parts from iGEM Registry</div>"
    for p in parts:
        role_tag = f"<span class='tag'>{p['role']}</span>" if p["role"] else ""
        status_tag = f"<span class='tag'>{p['status']}</span>" if p["status"] == "published" else ""
        html += (
            f"<a href='{p['url']}' target='_blank' class='source-row'>"
            f"<div class='src-num' style='color:var(--orange);min-width:80px;font-size:12px'>{p['name']}</div>"
            f"<div class='src-info'>"
            f"<div class='src-team'>{p['title']}</div>"
            f"<div class='src-meta'>{p['description'][:120]}...</div>"
            f"<div class='tags' style='margin-top:4px'>{role_tag}{status_tag}</div>"
            f"</div></a>"
        )
    return html
