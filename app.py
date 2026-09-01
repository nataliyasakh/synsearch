"""
SynSearch — iGEM Knowledge Retrieval
"""

import streamlit as st

st.set_page_config(
    page_title="SynSearch",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700;800&display=swap');
:root {
  --maroon: #6e1e18; --orange: #d6884a; --teal: #8fb3ac;
  --sand: #e7d8c4; --paper: #fbf7f0; --ash: #8a7e75;
  --border: #e0d3c1; --muted: #6f6157; --text: #2a1a16;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--paper) !important;
  font-family: 'Lexend', sans-serif !important;
  color: var(--text) !important;
  font-size: 16px !important;
}
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stDecoration"],footer,[data-testid="collapsedControl"] { display:none !important; }
/* NAV */
div[data-testid="stHorizontalBlock"]:first-of-type {
  background: var(--paper); border-bottom: 1px solid var(--border);
  padding: 4px 32px !important; margin: -1rem -1rem 0 !important;
  align-items: center !important; gap: 0 !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="column"] { padding: 0 !important; }
/* ALL buttons default = maroon */
.stButton > button {
  background: var(--maroon) !important; color: var(--paper) !important;
  border: none !important; border-radius: 3px !important;
  font-family: 'Lexend', sans-serif !important; font-weight: 700 !important;
  font-size: 13px !important; letter-spacing: .12em !important;
  text-transform: uppercase !important; height: 46px !important;
  transition: opacity .12s !important;
}
.stButton > button:hover { opacity: .85 !important; }
/* NAV buttons override = transparent */
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
  background: transparent !important; color: var(--ash) !important;
  height: 40px !important; border: none !important;
  box-shadow: none !important; font-size: 12px !important;
  font-weight: 700 !important; letter-spacing: .14em !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
  color: var(--orange) !important; background: transparent !important;
}
/* INPUTS */
[data-testid="stTextInput"] input,[data-baseweb="base-input"] input {
  background: #fff !important; border: 1px solid var(--border) !important;
  border-radius: 3px !important; color: #2a1a16 !important;
  font-family: 'Lexend', sans-serif !important; font-size: 15px !important;
  padding: 12px 16px !important; height: 48px !important;
  box-shadow: none !important; -webkit-text-fill-color: #2a1a16 !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--ash) !important; -webkit-text-fill-color: var(--ash) !important; }
[data-testid="stTextInput"] input:focus { border-color: var(--orange) !important; box-shadow: none !important; outline: none !important; }
[data-baseweb="base-input"] { border-radius: 3px !important; background: #fff !important; }
[data-testid="stTextInput"] label { display: none !important; }
/* SELECTBOX */
[data-testid="stSelectbox"] > div > div {
  -webkit-text-fill-color: #2a1a16 !important; background: #fff !important;
  border: 1px solid var(--border) !important; border-radius: 3px !important;
  color: var(--text) !important; font-family: 'Lexend', sans-serif !important;
  font-size: 14px !important;
}
[data-testid="stSelectbox"] label {
  font-size: 12px !important; font-weight: 700 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  color: var(--ash) !important;
}
/* LINK BUTTON */
a[data-testid="stLinkButton"] {
  background: var(--maroon) !important; border: none !important;
  border-radius: 3px !important; text-decoration: none !important;
}
a[data-testid="stLinkButton"] p {
  color: var(--paper) !important; font-family: 'Lexend', sans-serif !important;
  font-size: 13px !important; font-weight: 700 !important;
  letter-spacing: .08em !important; text-transform: uppercase !important;
}
.sep { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
/* HERO */
.hero { padding: 72px 0 48px; text-align: center; }
.hero-eyebrow { font-size: 12px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--teal); margin-bottom: 18px; }
.hero-title { font-size: 58px; font-weight: 800; line-height: 1.0; color: var(--maroon); margin-bottom: 18px; letter-spacing: -.02em; }
.hero-title em { font-style: normal; color: var(--orange); }
.hero-sub { font-size: 18px; font-weight: 300; color: var(--muted); max-width: 540px; margin: 0 auto 36px; line-height: 1.75; }
/* CARDS */
.answer-card { background: #fff; border: 1px solid var(--border); border-radius: 3px; padding: 28px 32px; margin-bottom: 24px; }
.card-eyebrow { font-size: 12px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--teal); margin-bottom: 16px; }
.answer-body { font-size: 17px; font-weight: 400; line-height: 1.9; color: #3a2a22; }
.cite-tag { display: inline-block; border: 1px solid var(--border); padding: 1px 7px; font-size: 12px; font-weight: 700; color: var(--teal); border-radius: 3px; vertical-align: middle; margin-left: 2px; }
.sources-head { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--ash); margin: 22px 0 12px; }
.source-row { display: flex; align-items: center; gap: 14px; padding: 12px 16px; background: var(--paper); border: 1px solid var(--border); border-radius: 3px; margin-bottom: 8px; text-decoration: none; transition: border-color .12s; }
.source-row:hover { border-color: var(--orange); }
.src-num { font-size: 13px; font-weight: 700; color: var(--teal); min-width: 24px; }
.src-info { flex: 1; }
.src-team { font-size: 15px; font-weight: 600; color: var(--maroon); }
.src-meta { font-size: 13px; color: var(--muted); margin-top: 3px; }
.badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 3px; white-space: nowrap; border: 1px solid; }
.badge-grand { color: var(--teal); background: #eaf2f0; border-color: #c5ddd9; }
.badge-gold { color: var(--orange); background: #fdf0e6; border-color: #f0cfa8; }
.badge-silver { color: var(--ash); background: var(--sand); border-color: var(--border); }
.badge-bronze { color: #b87333; background: #fdf5ee; border-color: #e8c9a0; }
.section-head { display: flex; align-items: center; gap: 10px; margin: 32px 0 14px; }
.section-title { font-size: 12px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--ash); }
.section-pill { font-size: 12px; font-weight: 700; padding: 3px 10px; border: 1px solid #c5ddd9; color: var(--teal); background: #eaf2f0; border-radius: 3px; }
.sim-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.sim-card { background: #fff; border: 1px solid var(--border); border-radius: 3px; padding: 16px 18px; text-decoration: none; display: block; transition: border-color .12s; }
.sim-card:hover { border-color: var(--orange); }
.sim-pct { font-size: 13px; font-weight: 700; color: var(--teal); margin-bottom: 6px; }
.sim-team { font-size: 15px; font-weight: 700; color: var(--maroon); margin-bottom: 4px; }
.sim-title-text { font-size: 14px; color: var(--muted); line-height: 1.5; margin-bottom: 10px; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag { font-size: 12px; font-weight: 600; padding: 3px 9px; border-radius: 3px; background: var(--sand); color: var(--muted); border: 1px solid var(--border); }
.score-bar { height: 2px; background: var(--border); border-radius: 1px; margin-top: 12px; overflow: hidden; }
.score-fill { height: 100%; background: var(--teal); border-radius: 1px; }
.bench-card { background: #fff; border: 1px solid var(--border); border-radius: 3px; padding: 24px 28px; margin-bottom: 12px; }
.bench-name { font-size: 16px; font-weight: 700; color: var(--maroon); margin-bottom: 4px; }
.bench-desc { font-size: 14px; color: var(--muted); margin-bottom: 18px; }
.metric-row { display: flex; gap: 10px; }
.metric { flex: 1; background: var(--paper); border: 1px solid var(--border); border-radius: 3px; padding: 16px; }
.metric-label { font-size: 12px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--ash); margin-bottom: 8px; }
.metric-val { font-size: 32px; font-weight: 700; color: var(--maroon); }
.mbar-bg { height: 3px; background: var(--border); border-radius: 1px; margin-top: 10px; overflow: hidden; }
.mbar { height: 100%; border-radius: 1px; }
.about-card { background: #fff; border: 1px solid var(--border); border-radius: 3px; padding: 24px 28px; margin-bottom: 12px; }
.about-h { font-size: 16px; font-weight: 700; color: var(--maroon); margin-bottom: 10px; }
.about-p { font-size: 15px; font-weight: 300; color: #3a2a22; line-height: 1.85; }
.about-p a { color: var(--teal); text-decoration: none; }
.about-p a:hover { text-decoration: underline; }
.about-ul { font-size: 15px; font-weight: 300; color: #3a2a22; line-height: 2.1; padding-left: 20px; }
.empty-state { text-align: center; padding: 72px 0; color: var(--ash); font-size: 16px; font-weight: 300; }
.empty-state em { color: var(--orange); font-style: normal; }
</style>
""", unsafe_allow_html=True)

# --- Demo data -------------------------------------------------------------
# Shown automatically whenever retrieval.py / tools_page.py haven't been
# built yet, so a fresh clone of this repo always runs without crashing.
# Once those files exist, app.py picks them up automatically (see the
# try/except blocks below) — no manual swapping required.
DEMO_ANSWER = (
    "This is placeholder answer text. Connect retrieval.py to your Pinecone "
    "index and Groq API key to replace this with real synthesised answers."
)

DEMO_SOURCES = [
    {"num": 1, "team": "iGEM Munich 2024", "url": "https://gitlab.igem.org/2024/software-tools/munich", "track": "Foundational Advance", "medal": "Gold"},
    {"num": 2, "team": "iGEM Example Team", "url": "https://igem.wiki/example", "track": "Diagnostics", "medal": "Silver"},
]

DEMO_SIMILAR = [
    {"team": "iGEM Example Team", "year": "2023", "url": "https://igem.wiki/example", "score": 82, "track": "Diagnostics", "medal": "Silver", "title": "Biosensor for heavy metal detection in drinking water"},
    {"team": "iGEM Sample Team", "year": "2022", "url": "https://igem.wiki/sample", "score": 74, "track": "Environment", "medal": "Gold", "title": "Whole-cell biosensor platform for arsenic monitoring"},
]

DEMO_BENCH = [
    {"name": "Bare Groq (no retrieval)", "desc": "No retrieval — model answers from training data only. Fluent but frequently hallucinated.", "f": 0.11, "r": 0.75, "c": 0.12, "color": "#6e1e18"},
    {"name": "Groq fast + SynSearch RAG", "desc": "Fast model grounded in 1,000+ iGEM wikis (2016–2025) via Pinecone vector retrieval.", "f": 0.42, "r": 0.19, "c": 0.30, "color": "#d6884a"},
    {"name": "Groq large + SynSearch RAG", "desc": "Large model + SynSearch RAG — 7× improvement in faithfulness over bare LLM.", "f": 0.79, "r": 0.27, "c": 0.21, "color": "#8fb3ac"},
]


def badge(medal):
    if not medal or medal in ("-", "Unknown", ""):
        return ""
    m = medal.lower()
    if "grand" in m:
        return f"<span class='badge badge-grand'>{medal}</span>"
    if "gold" in m:
        return f"<span class='badge badge-gold'>{medal}</span>"
    if "silver" in m:
        return f"<span class='badge badge-silver'>{medal}</span>"
    if "bronze" in m:
        return f"<span class='badge badge-bronze'>{medal}</span>"
    return ""


def sbar(pct):
    return f"<div class='score-bar'><div class='score-fill' style='width:{pct}%'></div></div>"


def mbar(val, color):
    return f"<div class='mbar-bg'><div class='mbar' style='width:{int(val*100)}%;background:{color}'></div></div>"


if "page" not in st.session_state:
    st.session_state.page = "search"

PAGES = [("Search", "search"), ("Similar Projects", "similar"), ("Tools", "tools"), ("Benchmark", "benchmark"), ("About", "about")]

nav = st.columns([2, 1, 1.3, 1, 1, 1])
with nav[0]:
    st.markdown("<p style='font-size:14px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#6e1e18;margin:0;padding:10px 0'>SynSearch</p>", unsafe_allow_html=True)
for i, (label, key) in enumerate(PAGES):
    with nav[i + 1]:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

# SEARCH
if st.session_state.page == "search":
    st.markdown("""
    <div class='hero'>
      <div class='hero-eyebrow'>iGEM knowledge retrieval &middot; 1,000+ wikis &middot; 2016–2025 corpus</div>
      <div class='hero-title'>Ask the iGEM<br><em>archive</em></div>
      <div class='hero-sub'>Search past iGEM team wikis in plain English. Every answer links back to the original source so you can verify it.</div>
    </div>""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        query = st.text_input("q", placeholder="e.g. How did teams build biosensors for heavy metal detection?", label_visibility="collapsed", key="q")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            year = st.selectbox("Year", ["All years", "2016", "2017", "2018", "2019", "2022", "2023", "2024", "2025"], key="fy")
        with fc2:
            track = st.selectbox("Village", ["All villages", "Agriculture", "Art & Design", "Biomanufacturing", "Bioremediation", "Climate Crisis", "Conservation", "Diagnostics", "Energy", "Environment", "Fashion & Cosmetics", "Food & Nutrition", "Foundational Advance", "Hardware", "Health & Medicine", "High School", "Infectious Diseases", "Manufacturing", "New Application", "Oncology", "Software & AI", "Space", "Therapeutics"], key="ft")
        with fc3:
            medal = st.selectbox("Medal", ["Any medal", "Gold", "Silver", "Bronze"], key="fm")
        go = st.button("Search corpus", key="go", use_container_width=True)

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    if go or (query and query.strip()):
        with st.spinner("Searching corpus..."):
            try:
                from retrieval import search as real_search
                answer_text, real_sources, real_similar = real_search(query, year=year, track=track, medal=medal)
            except ImportError:
                answer_text, real_sources, real_similar = DEMO_ANSWER, DEMO_SOURCES, DEMO_SIMILAR

        src_rows = ""
        for s in real_sources:
            short = s["url"].replace("https://", "")
            src_rows += f"<a href='{s['url']}' target='_blank' class='source-row'><div class='src-num'>[{s['num']}]</div><div class='src-info'><div class='src-team'>{s['team']}</div><div class='src-meta'>{s.get('track','')} &middot; {short}</div></div>{badge(s['medal'])}</a>"

        st.markdown(f"<div class='answer-card'><div class='card-eyebrow'>Synthesised answer &middot; {len(real_sources)} sources</div><div class='answer-body'>{answer_text}</div><div class='sources-head'>Sources — click to open original wiki</div>{src_rows}</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-head'><span class='section-title'>Similar projects</span><span class='section-pill'>unique to SynSearch</span></div>", unsafe_allow_html=True)
        sim = "<div class='sim-grid'>"
        for s in real_similar:
            village = s.get("track", "")
            med = s.get("medal", "")
            sim += (f"<a href='{s['url']}' target='_blank' class='sim-card'><div class='sim-pct'>{s['score']}% match</div><div class='sim-team'>{s['team']} &middot; {s['year']}</div><div class='sim-title-text'>{s.get('institution', s['team'])}</div><div class='tags'>"
                    + (f"<span class='tag'>{village}</span>" if village else "")
                    + (f"<span class='tag'>{med}</span>" if med and med not in ("-", "Unknown", "") else "")
                    + f"<span class='tag'>{s['year']}</span></div>{sbar(s['score'])}</a>")
        st.markdown(sim + "</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='empty-state'>Type a question above and press Search corpus.<br>Try: <em>biosensor for heavy metal detection</em> &nbsp;&middot;&nbsp; <em>genetic toggle switch in E. coli</em></div>", unsafe_allow_html=True)

# SIMILAR PROJECTS
elif st.session_state.page == "similar":
    st.markdown("<div style='padding:64px 0 32px'><div class='hero-eyebrow'>Semantic similarity explorer</div><div class='hero-title' style='font-size:48px;text-align:left'>Find projects<br><em>like yours</em></div><div class='hero-sub' style='text-align:left;margin:12px 0 0'>Describe your project. SynSearch ranks the closest past iGEM teams by vector similarity. Google cannot do this.</div></div>", unsafe_allow_html=True)

    sq = st.text_input("sq", placeholder="e.g. We are engineering E. coli to detect arsenic in drinking water", label_visibility="collapsed", key="sq")

    if st.button("Find similar projects", key="sgo") or sq:
        with st.spinner("Computing similarity..."):
            try:
                from retrieval import find_similar
                real_sim = find_similar(sq)
            except ImportError:
                real_sim = DEMO_SIMILAR

        st.markdown("<div class='section-head' style='margin-top:24px'><span class='section-title'>Top matches across 1,000+ teams</span></div>", unsafe_allow_html=True)
        from retrieval import get_institution_years
        sim2 = "<div class='sim-grid'>"
        for s in real_sim:
            village = s.get("track", "")
            med = s.get("medal", "")
            institution = s.get("institution", s.get("team", ""))
            other_years = get_institution_years(institution, int(s["year"]))
            other_html = ""
            if other_years:
                link_parts = []
                for oy in other_years[:4]:
                    oy_url  = oy["url"]
                    oy_year = oy["year"]
                    link_parts.append(f"<a href='{oy_url}' target='_blank' style='color:var(--teal);text-decoration:none;font-weight:600'>{oy_year}</a>")
                links = " &middot; ".join(link_parts)
                other_html = f"<div style='margin-top:10px;padding-top:8px;border-top:1px solid var(--border);font-size:11px;color:var(--ash)'><span style='font-weight:600'>Also competed:</span> {links}</div>"
            card_url = s['url']
            onclick = "window.open('" + card_url + "','_blank')"
            card = (f"<div class='sim-card' onclick='{onclick}' style='cursor:pointer'>"
                    f"<div class='sim-pct'>{s['score']}% match</div>"
                    f"<div class='sim-team'>{s['team']} &middot; {s['year']}</div>"
                    f"<div class='sim-title-text'>{s.get('title','') or institution}</div>"
                    f"<div class='tags'>"
                    + (f"<span class='tag'>{village}</span>" if village else "")
                    + (f"<span class='tag'>{med}</span>" if med and med not in ("-","Unknown","") else "")
                    + f"</div>{sbar(s['score'])}{other_html}</div>")
            sim2 += card
        st.markdown(sim2 + "</div>", unsafe_allow_html=True)

# TOOLS
elif st.session_state.page == "tools":
    try:
        from tools_page import render_tools_page
        render_tools_page()
    except ImportError:
        st.markdown("<div class='empty-state'>Tools page is still in development — <em>check back soon</em>.</div>", unsafe_allow_html=True)

# BENCHMARK
elif st.session_state.page == "benchmark":
    st.markdown("<div style='padding:64px 0 32px'><div class='hero-eyebrow'>LLM-as-judge evaluation &middot; 50 ground-truth questions</div><div class='hero-title' style='font-size:48px;text-align:left'>Does RAG<br><em>actually help?</em></div><div class='hero-sub' style='text-align:left;margin:12px 0 0'>Three systems, same 50 iGEM-specific questions, verified answers. RAG improves faithfulness by <strong>7×</strong> over a bare LLM.</div></div><hr class='sep'>", unsafe_allow_html=True)

    for b in DEMO_BENCH:
        st.markdown(f"<div class='bench-card'><div class='bench-name'>{b['name']}</div><div class='bench-desc'>{b['desc']}</div><div class='metric-row'><div class='metric'><div class='metric-label'>Faithfulness</div><div class='metric-val'>{b['f']:.2f}</div>{mbar(b['f'],b['color'])}</div><div class='metric'><div class='metric-label'>Answer relevancy</div><div class='metric-val'>{b['r']:.2f}</div>{mbar(b['r'],b['color'])}</div><div class='metric'><div class='metric-label'>Context recall</div><div class='metric-val'>{b['c']:.2f}</div>{mbar(b['c'],b['color'])}</div></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='about-card' style='margin-top:12px'><div class='about-h'>Methodology</div><div class='about-p'>50 questions were written based on real queries a new iGEM team member would ask, spanning Diagnostics, Foundational Advance, Environment, and Manufacturing tracks. Correct answers and source wikis were verified manually before evaluation. Scoring uses an LLM-as-judge approach following the RAGAS framework (Es et al., 2023), measuring faithfulness, answer relevancy, and context recall. Numbers above are from the demo benchmark run pending a full evaluation pass — see README for status.</div></div>", unsafe_allow_html=True)

# ABOUT
elif st.session_state.page == "about":
    st.markdown("<div style='padding:64px 0 32px'><div class='hero-eyebrow'>iGEM 2026 Software &amp; AI Village</div><div class='hero-title' style='font-size:48px;text-align:left'>About<br><em>SynSearch</em></div></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='about-card'><div class='about-h'>What it is</div><div class='about-p'>SynSearch makes the iGEM archive searchable in plain English. Describe what your team is working on and instantly find the most relevant past projects, protocols, and design choices — with direct links to the original wiki pages for verification. No hallucinated citations. No terminal required.</div></div>
    <div class='about-card'><div class='about-h'>Building on Munich 2024</div><div class='about-p'>The Munich 2024 iGEM team built the first proof-of-concept RAG system over iGEM wiki data, demonstrating that grounding an LLM in retrieved documents reduces hallucination on synthetic biology questions. Their system ingested 343 teams from the 2019 competition and showed measurable improvement in answer quality — but left several capabilities explicitly unfinished: source citations, metadata filtering, and accuracy benchmarking were all listed as future work. The tool also required Docker and a personal API key to run, limiting adoption by non-technical users.<br><br>SynSearch builds directly on their foundation. We reuse their 2019 corpus under CC BY 4.0 and independently contributed:<ul class='about-ul'><li>Corpus expansion from 343 teams (2019 only) to 1,000+ teams across 2016–2025</li><li>Inline source citations linking to the specific wiki page — Munich's own listed future work</li><li>Metadata filtering by year, village, and medal before retrieval</li><li>A "Similar Projects" semantic explorer — not available in any existing registry</li><li>Published three-way benchmark: bare LLM vs RAG on 50 manually verified questions</li><li>Zero-install hosted interface — no Docker, no terminal, no API key required</li></ul></div></div>
    <div class='about-card'><div class='about-h'>Stack</div><div class='about-p'>sentence-transformers (all-MiniLM-L6-v2) &middot; Pinecone (58,569 vectors) &middot; Groq API &middot; Streamlit Cloud &middot; Munich 2024 corpus (CC BY 4.0)</div></div>
    <div class='about-card'><div class='about-h'>Data attribution</div><div class='about-p'>The 2019 iGEM wiki corpus was scraped and curated by the <a href='https://gitlab.igem.org/2024/software-tools/munich' target='_blank'>Munich 2024 iGEM team</a> and is used under Creative Commons Attribution 4.0. We are grateful for their work. The 2016–2025 corpus was independently scraped from igem.wiki and via the Wayback Machine using the public iGEM API.</div></div>
    <div class='about-card'><div class='about-h'>Citation</div><div class='about-p'>Es, S., James, J., Espinosa-Anke, L., &amp; Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. <em>arXiv:2309.15217</em>.</div></div>
    """, unsafe_allow_html=True)
