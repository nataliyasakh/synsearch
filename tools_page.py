"""
tools_page.py — render the Tools page in app.py.
"""

import re
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

def md_to_html(text):
    """Convert markdown bold/italic to HTML and preserve line breaks."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'^(\d+)\.\s+', r'<br><strong>\1.</strong> ', text, flags=re.MULTILINE)
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return text

def render_tools_page():
    st.markdown("""
    <style>
    .tool-card {
      background: #fff; border: 1px solid var(--border);
      border-radius: 3px; padding: 20px 22px; margin-bottom: 12px;
      text-decoration: none; display: block; transition: border-color .12s;
    }
    .tool-card:hover { border-color: var(--orange); }
    .tool-card-header {
      display: flex; justify-content: space-between;
      align-items: flex-start; margin-bottom: 8px; gap: 12px;
    }
    .tool-name { font-size: 16px; font-weight: 700; color: var(--maroon); }
    .tool-cat {
      font-size: 11px; font-weight: 600; padding: 3px 9px;
      border-radius: 3px; background: var(--sand); color: var(--muted);
      border: 1px solid var(--border); white-space: nowrap;
      display: inline-block; margin-top: 8px;
    }
    .tool-desc {
      font-size: 14px; font-weight: 300; color: #3a2a22;
      line-height: 1.75; margin: 10px 0 10px;
    }
    .tool-io { font-size: 12px; color: var(--teal); font-weight: 500; }
    .tool-free-yes {
      font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px;
      color: var(--teal); background: #eaf2f0; border: 1px solid #c5ddd9;
      white-space: nowrap;
    }
    .tool-free-no {
      font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 3px;
      color: var(--ash); background: var(--sand); border: 1px solid var(--border);
      white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:56px 0 28px'>
      <div class='hero-eyebrow'>40 verified tools &middot; used by iGEM teams worldwide</div>
      <div class='hero-title' style='font-size:48px;text-align:left'>
        Find the right<br><em>tool for the job</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0'>
        Describe what you need to do. SynSearch recommends the best tools
        and shows how real iGEM teams used them.
      </div>
    </div>
    """, unsafe_allow_html=True)

    tool_query = st.text_input(
        "tool_q",
        placeholder="e.g.  I need to design primers for Gibson Assembly cloning",
        label_visibility="collapsed",
        key="tool_query"
    )

    fc1, fc2 = st.columns([3, 1])
    with fc1:
        category = st.selectbox("Category", CATEGORIES, key="tool_cat")
    with fc2:
        free_only = st.checkbox("Free only", key="tool_free", value=False)

    search_btn = st.button("Find tools", key="tool_go", use_container_width=True)

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    df = load_tools()

    filtered = df.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if free_only:
        filtered = filtered[
            filtered["free"].str.lower().str.contains("yes|free", na=False)
        ]

    if tool_query or search_btn:
        with st.spinner("Finding best tools..."):
            tools_context = filtered[["name","category","use_case","description","free"]].to_string(index=False)
            try:
                from groq import Groq
                import tomllib
                from pathlib import Path
                with open(Path(".streamlit/secrets.toml"), "rb") as f:
                    secrets = tomllib.load(f)
                groq_client = Groq(api_key=secrets["GROQ_API_KEY"])
                response = groq_client.chat.completions.create(
                    model="groq/compound-mini",
                    messages=[
                        {"role": "system", "content": (
                            "You are a synthetic biology expert helping iGEM teams choose software tools. "
                            "Recommend the TOP 3 most relevant tools for the user's task from the database. "
                            "For each tool: state the name, explain in 1-2 sentences why it fits, mention one specific feature. "
                            "Do NOT use markdown asterisks. Write in plain text with numbered list format."
                        )},
                        {"role": "user", "content": "Task: " + tool_query + "\n\nAvailable tools:\n" + tools_context}
                    ],
                    temperature=0.1,
                    max_tokens=500,
                )
                ai_rec = response.choices[0].message.content.strip()
                ai_html = md_to_html(ai_rec)
            except Exception as e:
                ai_html = f"Could not generate recommendation ({e}). Browse tools below."

        st.markdown(
            "<div class='answer-card'>"
            "<div class='card-eyebrow'>AI recommendation &middot; from " + str(len(filtered)) + " tools</div>"
            "<div class='answer-body'>" + ai_html + "</div>"
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class='section-head'>
          <span class='section-title'>How iGEM teams used these tools</span>
          <span class='section-pill'>from 1,000+ wikis</span>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Searching iGEM wikis..."):
            try:
                from retrieval import search as real_search
                wiki_answer, wiki_sources, _ = real_search(
                    "how did iGEM teams use " + tool_query
                )
                src_rows = ""
                for s in wiki_sources:
                    short = s["url"].replace("https://", "")
                    src_rows += (
                        "<a href='" + s["url"] + "' target='_blank' class='source-row'>"
                        "<div class='src-num'>[" + str(s["num"]) + "]</div>"
                        "<div class='src-info'>"
                        "<div class='src-team'>" + s["team"] + "</div>"
                        "<div class='src-meta'>" + s.get("track","") + " &middot; " + short + "</div>"
                        "</div></a>"
                    )
                st.markdown(
                    "<div class='answer-card'>"
                    "<div class='answer-body'>" + wiki_answer + "</div>"
                    "<div class='sources-head'>Source wikis</div>"
                    + src_rows + "</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.markdown(
                    "<div class='answer-card'><div class='answer-body'>Wiki search temporarily unavailable.</div></div>",
                    unsafe_allow_html=True
                )

        st.markdown("""
        <div class='section-head' style='margin-top:28px'>
          <span class='section-title'>All matching tools</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(
            "<div class='section-head'><span class='section-title'>"
            + str(len(filtered)) + " tools</span></div>",
            unsafe_allow_html=True
        )

    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        free_str = str(row["free"]).lower()
        if "yes" in free_str or ("free" in free_str and "igem" not in free_str and "freemium" not in free_str):
            free_badge = "<span class='tool-free-yes'>Free</span>"
        elif "igem" in free_str:
            free_badge = "<span class='tool-free-yes'>Free for iGEM</span>"
        elif "freemium" in free_str:
            free_badge = "<span class='tool-free-no'>Freemium</span>"
        else:
            free_badge = "<span class='tool-free-no'>Paid</span>"

        with cols[i % 2]:
            st.markdown(
                "<a href='" + str(row["url"]) + "' target='_blank' class='tool-card'>"
                "<div class='tool-card-header'>"
                "<div class='tool-name'>" + str(row["name"]) + "</div>"
                + free_badge +
                "</div>"
                "<span class='tool-cat'>" + str(row["category"]) + "</span>"
                "<div class='tool-desc'>" + str(row["description"]) + "</div>"
                "<div class='tool-io'>Input: " + str(row["input"]) + " &rarr; Output: " + str(row["output"]) + "</div>"
                "</a>",
                unsafe_allow_html=True
            )
