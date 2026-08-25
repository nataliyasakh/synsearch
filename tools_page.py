"""
tools_page.py — Tools page for SynSearch.
Clean design matching the rest of the app.
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
    return ''.join(
        '<p style="margin:0 0 12px;font-size:16px;line-height:1.8">'
        + p.replace('\n', '<br>') + '</p>'
        for p in paragraphs
    )

def render_tools_page():
    # Override link_button color to match app theme
    st.markdown("""
    <style>
    a[data-testid="stLinkButton"] > div > p {
      font-size: 13px !important;
      font-weight: 700 !important;
      letter-spacing: .08em !important;
      text-transform: uppercase !important;
    }
    a[data-testid="stLinkButton"] {
      background: var(--maroon) !important;
      border: none !important;
      border-radius: 3px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      border-color: var(--border) !important;
      border-radius: 3px !important;
      background: #fff !important;
      padding: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:48px 0 24px'>
      <div class='hero-eyebrow'>40 verified tools &middot; used by iGEM teams worldwide</div>
      <div class='hero-title' style='font-size:52px;text-align:left'>
        Find the right<br><em>tool for the job</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0;font-size:18px'>
        Describe what you need to do. SynSearch recommends the best tools
        and shows how real iGEM teams used them.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Search
    tool_query = st.text_input(
        "tool_q", label_visibility="collapsed", key="tool_query",
        placeholder="e.g.  I need to design primers for Gibson Assembly cloning"
    )

    col_a, col_b, col_c = st.columns([3, 1, 1])
    with col_a:
        category = st.selectbox("Category", CATEGORIES, key="tool_cat")
    with col_b:
        free_filter = st.selectbox("Price", ["All tools", "Free only"], key="tool_free", label_visibility="visible")
        free_only = (free_filter == "Free only")

    search_btn = st.button("Find tools", key="tool_go", use_container_width=True)
    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    # Load & filter
    df = load_tools()
    filtered = df.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if free_only:
        filtered = filtered[filtered["free"].str.lower().str.contains("yes|free", na=False)]

    # AI + wiki
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
                            "You are a synthetic biology expert helping iGEM teams choose tools. "
                            "Recommend TOP 3 tools from the database for the user's task. "
                            "Write plain numbered list. No asterisks or markdown. "
                            "For each: tool name, why it fits (1 sentence), key feature (1 sentence)."
                        )},
                        {"role": "user", "content": "Task: " + tool_query + "\n\nTools:\n" + tools_ctx}
                    ],
                    temperature=0.1, max_tokens=500,
                )
                ai_html = md_to_html(resp.choices[0].message.content.strip())
            except Exception as e:
                ai_html = "<p>Could not generate recommendation. Browse tools below.</p>"

        st.markdown(
            "<div class='answer-card'>"
            "<div class='card-eyebrow'>AI recommendation</div>"
            "<div class='answer-body'>" + ai_html + "</div>"
            "</div>",
            unsafe_allow_html=True
        )

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
                src_html = "".join(
                    "<a href='" + s["url"] + "' target='_blank' class='source-row'>"
                    "<div class='src-num'>[" + str(s["num"]) + "]</div>"
                    "<div class='src-info'><div class='src-team'>" + s["team"] + "</div>"
                    "<div class='src-meta'>" + s.get("track","") + " &middot; " + s["url"].replace("https://","") + "</div>"
                    "</div></a>"
                    for s in wiki_sources
                )
                st.markdown(
                    "<div class='answer-card'><div class='answer-body'>" + wiki_answer + "</div>"
                    "<div class='sources-head'>Source wikis</div>" + src_html + "</div>",
                    unsafe_allow_html=True
                )
            except:
                st.markdown("<div class='answer-card'><div class='answer-body'>Wiki search temporarily unavailable.</div></div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='section-head' style='margin-top:28px'>"
            "<span class='section-title'>All " + str(len(filtered)) + " matching tools</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='section-head'><span class='section-title'>"
            + str(len(filtered)) + " tools</span></div>",
            unsafe_allow_html=True
        )

    # Tool cards — 2 per row using native containers
    tool_list = list(filtered.iterrows())
    for i in range(0, len(tool_list), 2):
        cols = st.columns(2, gap="medium")
        for j in range(2):
            if i + j >= len(tool_list):
                break
            _, tool = tool_list[i + j]
            free_str = str(tool["free"]).lower()
            if "freemium" in free_str:
                fb = "<span class='badge badge-silver'>Freemium</span>"
            elif "igem" in free_str:
                fb = "<span class='badge badge-grand'>Free for iGEM</span>"
            elif "yes" in free_str or ("free" in free_str and "paid" not in free_str):
                fb = "<span class='badge badge-grand'>Free</span>"
            else:
                fb = "<span class='badge badge-silver'>Paid</span>"

            with cols[j]:
                st.markdown(
                    "<div class='answer-card' style='min-height:220px'>"
                    "<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>"
                    "<div class='src-team' style='font-size:17px'>" + str(tool["name"]) + "</div>"
                    + fb +
                    "</div>"
                    "<span class='tag' style='font-size:12px'>" + str(tool["category"]) + "</span>"
                    "<div style='font-size:15px;font-weight:300;color:#3a2a22;line-height:1.75;margin:12px 0 10px'>"
                    + str(tool["description"]) +
                    "</div>"
                    "<div style='font-size:13px;color:var(--teal);font-weight:500'>"
                    "Input: " + str(tool["input"]) + " &rarr; Output: " + str(tool["output"]) +
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
                st.link_button(
                    "Open " + str(tool["name"]) + " →",
                    str(tool["url"]),
                    use_container_width=True
                )
