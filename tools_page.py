"""
tools_page.py — Tools page for SynSearch.
Uses native Streamlit layout to avoid HTML card overlap issues.
"""

import re
import pandas as pd
import streamlit as st

@st.cache_data
def load_tools():
    return pd.read_csv("tools.csv")

CATEGORIES = [
    "All categories",
    "Sequence Design", "Expression Design", "Cloning Design",
    "CRISPR Design", "Protein Structure", "Protein Modeling",
    "Protein Visualization", "Modeling", "Sequence Analysis",
    "Parts & Registry", "Fluorescent Proteins", "Lab Management",
]

def md_to_html(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    paragraphs = text.strip().split('\n\n')
    return ''.join(f'<p style="margin:0 0 10px">{p.replace(chr(10), "<br>")}</p>' for p in paragraphs)

def free_badge(free_str):
    s = str(free_str).lower()
    if "freemium" in s:
        return "<span class='badge badge-silver'>Freemium</span>"
    if "igem" in s:
        return "<span class='badge badge-grand'>Free for iGEM</span>"
    if "yes" in s or "free" in s:
        return "<span class='badge badge-grand'>Free</span>"
    return "<span class='badge badge-silver'>Paid</span>"

def render_tools_page():
    st.markdown("""
    <div style='padding:48px 0 24px'>
      <div class='hero-eyebrow'>40 verified tools &middot; used by iGEM teams worldwide</div>
      <div class='hero-title' style='font-size:48px;text-align:left'>
        Find the right<br><em>tool for the job</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:10px 0 0'>
        Describe what you need to do. SynSearch recommends the best tools
        and shows how real iGEM teams used them.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Search controls ────────────────────────────────────────────────────────
    tool_query = st.text_input(
        "tool_q",
        placeholder="e.g.  I need to design primers for Gibson Assembly cloning",
        label_visibility="collapsed",
        key="tool_query"
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        category = st.selectbox("Category", CATEGORIES, key="tool_cat",
                                label_visibility="visible")
    with c2:
        free_only = st.toggle("Free only", key="tool_free", value=False)
    with c3:
        search_btn = st.button("Find tools", key="tool_go", use_container_width=True)

    st.divider()

    # ── Load & filter ──────────────────────────────────────────────────────────
    df = load_tools()
    filtered = df.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if free_only:
        filtered = filtered[
            filtered["free"].str.lower().str.contains("yes|free", na=False)
        ]

    # ── AI recommendation + wiki context ───────────────────────────────────────
    if tool_query or search_btn:
        with st.spinner("Finding best tools..."):
            tools_ctx = filtered[["name","category","use_case","description","free"]].to_string(index=False)
            try:
                from groq import Groq
                import tomllib
                from pathlib import Path
                with open(Path(".streamlit/secrets.toml"), "rb") as f:
                    s = tomllib.load(f)
                client = Groq(api_key=s["GROQ_API_KEY"])
                resp = client.chat.completions.create(
                    model="groq/compound-mini",
                    messages=[
                        {"role": "system", "content": (
                            "You are a synthetic biology expert helping iGEM teams choose software tools. "
                            "Recommend TOP 3 tools for the user's task from the provided database. "
                            "Write in plain numbered list. No markdown asterisks. "
                            "For each: name, one sentence why it fits, one key feature."
                        )},
                        {"role": "user", "content": "Task: " + tool_query + "\n\nTools:\n" + tools_ctx}
                    ],
                    temperature=0.1, max_tokens=500,
                )
                ai_text = resp.choices[0].message.content.strip()
                ai_html = md_to_html(ai_text)
            except Exception as e:
                ai_html = "Could not generate recommendation. Browse tools below."

        st.markdown(
            "<div class='answer-card'>"
            "<div class='card-eyebrow'>AI recommendation</div>"
            "<div class='answer-body'>" + ai_html + "</div>"
            "</div>",
            unsafe_allow_html=True
        )

        # Wiki context
        st.markdown(
            "<div class='section-head'>"
            "<span class='section-title'>How iGEM teams used these tools</span>"
            "<span class='section-pill'>from 1,000+ wikis</span>"
            "</div>",
            unsafe_allow_html=True
        )
        with st.spinner("Searching iGEM wikis..."):
            try:
                from retrieval import search as real_search
                wiki_answer, wiki_sources, _ = real_search("how did iGEM teams use " + tool_query)
                src_html = ""
                for s in wiki_sources:
                    short = s["url"].replace("https://", "")
                    src_html += (
                        "<a href='" + s["url"] + "' target='_blank' class='source-row'>"
                        "<div class='src-num'>[" + str(s["num"]) + "]</div>"
                        "<div class='src-info'><div class='src-team'>" + s["team"] + "</div>"
                        "<div class='src-meta'>" + s.get("track","") + " &middot; " + short + "</div>"
                        "</div></a>"
                    )
                st.markdown(
                    "<div class='answer-card'><div class='answer-body'>" + wiki_answer + "</div>"
                    "<div class='sources-head'>Source wikis</div>" + src_html + "</div>",
                    unsafe_allow_html=True
                )
            except:
                st.markdown(
                    "<div class='answer-card'><div class='answer-body'>Wiki search temporarily unavailable.</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown(
            "<div class='section-head' style='margin-top:24px'>"
            "<span class='section-title'>All " + str(len(filtered)) + " matching tools</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='section-head'>"
            "<span class='section-title'>" + str(len(filtered)) + " tools</span></div>",
            unsafe_allow_html=True
        )

    # ── Tool cards using native Streamlit ─────────────────────────────────────
    rows = [filtered.iloc[i:i+2] for i in range(0, len(filtered), 2)]
    for row_df in rows:
        cols = st.columns(2)
        for j, (_, tool) in enumerate(row_df.iterrows()):
            with cols[j]:
                with st.container(border=True):
                    # Header row
                    h1, h2 = st.columns([3, 1])
                    with h1:
                        st.markdown(
                            f"<div class='src-team' style='font-size:15px'>{tool['name']}</div>",
                            unsafe_allow_html=True
                        )
                    with h2:
                        st.markdown(
                            free_badge(tool["free"]),
                            unsafe_allow_html=True
                        )
                    # Category tag
                    st.markdown(
                        f"<span class='tag'>{tool['category']}</span>",
                        unsafe_allow_html=True
                    )
                    # Description — full, no truncation
                    st.markdown(
                        f"<div class='about-p' style='margin-top:8px;font-size:13px'>{tool['description']}</div>",
                        unsafe_allow_html=True
                    )
                    # Input/Output
                    st.markdown(
                        f"<div class='tool-io' style='font-size:12px;color:var(--teal);margin-top:6px'>"
                        f"Input: {tool['input']} &rarr; Output: {tool['output']}</div>",
                        unsafe_allow_html=True
                    )
                    # Link button
                    st.link_button("Open tool →", tool["url"], use_container_width=True)
