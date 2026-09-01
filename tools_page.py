"""
tools_page.py — Tools page for SynSearch.
"""
import re
import pandas as pd
import streamlit as st

@st.cache_data(ttl=0)
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
    st.markdown("""
    <style>
    a[data-testid="stLinkButton"] {
      background: var(--maroon) !important;
      border: none !important;
      border-radius: 3px !important;
    }
    a[data-testid="stLinkButton"] p {
      color: var(--paper) !important;
      font-family: 'Lexend', sans-serif !important;
      font-size: 13px !important;
      font-weight: 700 !important;
      letter-spacing: .08em !important;
      text-transform: uppercase !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='padding:48px 0 24px'>
      <div class='hero-eyebrow'>59 verified tools &middot; used by iGEM teams worldwide</div>
      <div class='hero-title' style='font-size:52px;text-align:left'>
        Find the right<br><em>tool for the job</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0;font-size:18px'>
        Describe what you need to do. SynSearch recommends the best tools
        and shows how real iGEM teams used them.
      </div>
    </div>
    """, unsafe_allow_html=True)

    tool_query = st.text_input(
        "tool_q", label_visibility="collapsed", key="tool_query",
        placeholder="e.g.  I need to design primers for Gibson Assembly cloning"
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        category = st.selectbox("Category", CATEGORIES, key="tool_cat", label_visibility="visible")
    with c2:
        price_filter = st.selectbox("Price", ["All tools", "Free only"], key="tool_free", label_visibility="visible")

    free_only = (price_filter == "Free only")
    search_btn = st.button("Find tools", key="tool_go", use_container_width=True)
    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    df = load_tools()
    filtered = df.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if free_only:
        filtered = filtered[filtered["free"].str.lower().str.contains("yes|free", na=False)]

    # Only show AI + wiki if user actually typed something
    if search_btn and tool_query.strip():
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
                            "Recommend TOP 3 tools from the database for the task. "
                            "Write a plain numbered list. No asterisks. No markdown. "
                            "For each tool write exactly 2 sentences: why it fits this task, and one specific feature. "
                            "Be direct and concise. Total response under 150 words."
                        )},
                        {"role": "user", "content": "Task: " + tool_query + "\n\nTools:\n" + tools_ctx}
                    ],
                    temperature=0.1, max_tokens=500,
                )
                ai_html = md_to_html(resp.choices[0].message.content.strip())
            except Exception as e:
                ai_html = "<p>Recommendation temporarily unavailable. Browse tools below.</p>"

        # Extract tool names mentioned in the recommendation
        import re as _re
        recommended_names = []
        for _, row in filtered.iterrows():
            if str(row['name']).lower() in resp.choices[0].message.content.lower():
                recommended_names.append(str(row['name']))
        st.session_state['tool_recommended'] = recommended_names
        st.session_state['tool_query_used'] = tool_query

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
        import time
        time.sleep(8)
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
        except Exception as e:
            st.markdown(
                "<div class='answer-card'><div class='answer-body' style='color:var(--ash)'>Wiki context temporarily unavailable.</div></div>",
                unsafe_allow_html=True
            )

        # Filter grid to recommended tools only
        if recommended_names:
            display_df = filtered[filtered['name'].isin(recommended_names)]
            grid_label = str(len(display_df)) + " recommended tools"
        else:
            display_df = filtered.head(6)
            grid_label = "Top tools in this category"

        st.markdown(
            "<div class='section-head' style='margin-top:28px'>"
            "<span class='section-title'>" + grid_label + "</span></div>",
            unsafe_allow_html=True
        )

    elif not tool_query.strip() and search_btn:
        st.warning("Please type what you need to do before searching.")
        st.markdown(
            "<div class='section-head'><span class='section-title'>"
            + str(len(filtered)) + " tools</span></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='section-head'><span class='section-title'>"
            + str(len(filtered)) + " tools — type a task above for AI recommendations</span></div>",
            unsafe_allow_html=True
        )

    # Tool cards — strict 2 per row
    # Use display_df if set (search mode), else show all filtered
    recommended = st.session_state.get('tool_recommended', [])
    last_query = st.session_state.get('tool_query_used', '')
    if recommended and last_query:
        grid_data = filtered[filtered['name'].isin(recommended)]
        if len(grid_data) == 0:
            grid_data = filtered
    else:
        grid_data = filtered
    tool_list = list(grid_data.iterrows())
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
                    "<div class='answer-card'>"
                    "<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>"
                    "<div class='src-team' style='font-size:17px'>" + str(tool["name"]) + "</div>"
                    + fb +
                    "</div>"
                    "<span class='tag' style='font-size:12px'>" + str(tool["category"]) + "</span>"
                    "<div style='font-size:15px;font-weight:300;color:#3a2a22;line-height:1.75;margin:12px 0 8px'>"
                    + str(tool["description"]) +
                    "</div>"
                    "<div style='font-size:13px;color:var(--teal);font-weight:500;margin-bottom:10px'>"
                    "Input: " + str(tool["input"]) + " &rarr; Output: " + str(tool["output"]) +
                    "</div>"
                    "<div style='font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#8a7e75;margin-bottom:6px'>How to use in iGEM</div>"
                    "<div style='font-size:13px;font-weight:300;color:#4a3a32;line-height:1.7'>"
                    + str(tool.get("how_to_use", "")) +
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )
                st.link_button(
                    "Open " + str(tool["name"]) + " →",
                    str(tool["url"]),
                    use_container_width=True
                )
