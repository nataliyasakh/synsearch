"""
tools_page.py — render the Tools page in app.py.

Call render_tools_page() from app.py when page == "tools".
Requires tools.csv in the same directory.
"""

import pandas as pd
import streamlit as st

@st.cache_data
def load_tools():
    return pd.read_csv("tools.csv")

CATEGORIES = [
    "All categories",
    "Sequence Design",
    "Expression Design",
    "Cloning Design",
    "CRISPR Design",
    "Protein Structure",
    "Protein Modeling",
    "Protein Visualization",
    "Modeling",
    "Sequence Analysis",
    "Parts & Registry",
    "Fluorescent Proteins",
    "Lab Management",
]

def render_tools_page():
    st.markdown("""
    <div style='padding:64px 0 32px'>
      <div class='hero-eyebrow'>40 verified tools &middot; used by iGEM teams worldwide</div>
      <div class='hero-title' style='font-size:48px;text-align:left'>
        Find the right<br><em>tool for the job</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0'>
        Describe what you need to do and SynSearch recommends the best tools —
        then shows how real iGEM teams used them.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI-powered tool search ─────────────────────────────────────────────────
    tool_query = st.text_input(
        "tool_q",
        placeholder="e.g.  I need to design primers for Gibson Assembly cloning",
        label_visibility="collapsed",
        key="tool_query"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        category = st.selectbox("Category", CATEGORIES, key="tool_cat")
    with col2:
        free_only = st.checkbox("Free tools only", key="tool_free")

    search_btn = st.button("Find tools", key="tool_go", use_container_width=False)

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    df = load_tools()

    if tool_query or search_btn:
        with st.spinner("Finding best tools..."):
            # Filter by category and free
            filtered = df.copy()
            if category != "All categories":
                filtered = filtered[filtered["category"] == category]
            if free_only:
                filtered = filtered[filtered["free"].str.lower().str.contains("yes|free")]

            # AI recommendation
            tools_context = filtered.to_string(index=False)

            from groq import Groq
            import os, tomllib
            from pathlib import Path

            with open(Path(".streamlit/secrets.toml"), "rb") as f:
                secrets = tomllib.load(f)
            groq_client = Groq(api_key=secrets["GROQ_API_KEY"])

            system_prompt = """You are a synthetic biology expert helping iGEM teams choose the right software tools.
Given a database of verified tools, recommend the TOP 3 most relevant tools for the user's task.

For each tool:
1. State the tool name clearly
2. Explain in 1-2 sentences WHY it fits this specific task
3. Mention one specific feature that makes it ideal

Format your response as:
**[Tool Name]** — [why it fits] [specific feature]

Only recommend tools from the provided database. Be specific and practical."""

            response = groq_client.chat.completions.create(
                model="groq/compound-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Task: {tool_query}\n\nAvailable tools:\n{tools_context}\n\nRecommend the top 3 tools for this task:"}
                ],
                temperature=0.1,
                max_tokens=400,
            )

            ai_recommendation = response.choices[0].message.content.strip()

        # Show AI recommendation
        st.markdown(f"""
        <div class='answer-card'>
          <div class='card-eyebrow'>AI recommendation &middot; based on {len(filtered)} tools</div>
          <div class='answer-body'>{ai_recommendation}</div>
        </div>
        """, unsafe_allow_html=True)

        # Show how iGEM teams used these tools
        st.markdown("""
        <div class='section-head'>
          <span class='section-title'>How iGEM teams used these tools</span>
          <span class='section-pill'>from the corpus</span>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Searching iGEM wikis..."):
            from retrieval import search as real_search
            wiki_query = f"how did iGEM teams use {tool_query}"
            wiki_answer, wiki_sources, _ = real_search(wiki_query)

        src_rows = ""
        for s in wiki_sources:
            short = s["url"].replace("https://", "")
            src_rows += (
                f"<a href='{s['url']}' target='_blank' class='source-row'>"
                f"<div class='src-num'>[{s['num']}]</div>"
                f"<div class='src-info'>"
                f"<div class='src-team'>{s['team']}</div>"
                f"<div class='src-meta'>{s.get('track','')} &middot; {short}</div>"
                f"</div></a>"
            )

        st.markdown(
            f"<div class='answer-card' style='margin-top:0'>"
            f"<div class='answer-body'>{wiki_answer}</div>"
            f"<div class='sources-head'>Source wikis</div>"
            f"{src_rows}</div>",
            unsafe_allow_html=True
        )

        # ── Full filtered tool grid ────────────────────────────────────────────
        st.markdown("""
        <div class='section-head' style='margin-top:32px'>
          <span class='section-title'>All matching tools</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Browse all tools
        filtered = df.copy()
        if category != "All categories":
            filtered = filtered[filtered["category"] == category]
        if free_only:
            filtered = filtered[filtered["free"].str.lower().str.contains("yes|free")]

        st.markdown(f"""
        <div class='section-head'>
          <span class='section-title'>{len(filtered)} tools</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Tool grid ──────────────────────────────────────────────────────────────
    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            free_badge = (
                "<span class='badge badge-grand'>Free</span>" if "yes" in str(row["free"]).lower()
                else "<span class='badge badge-silver'>Freemium</span>" if "freemium" in str(row["free"]).lower()
                else "<span class='badge badge-silver'>Free for iGEM</span>" if "igem" in str(row["free"]).lower()
                else "<span class='badge badge-silver'>Paid</span>"
            )
            st.markdown(f"""
            <a href='{row["url"]}' target='_blank' class='sim-card' style='margin-bottom:10px'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px'>
                <div class='sim-team'>{row["name"]}</div>
                {free_badge}
              </div>
              <div class='tag' style='margin-bottom:8px;display:inline-block'>{row["category"]}</div>
              <div class='sim-title-text'>{row["description"][:120]}...</div>
              <div style='font-size:12px;color:var(--teal);margin-top:6px'>
                Input: {row["input"]} &rarr; Output: {row["output"]}
              </div>
            </a>
            """, unsafe_allow_html=True)
