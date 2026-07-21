"""
SynSearch — iGEM Knowledge Retrieval System
Demo / template version: runs fully on demo data with no backend.
Replace the DEMO_* constants at the bottom with real retrieval calls
once the Chroma index is built.

Run:  streamlit run app.py
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="SynSearch",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS — Dunelock-inspired palette adapted for dark synbio aesthetic ──
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Lexend:wght@300;400;500;600&display=swap');

/* ── Token layer ── */
:root {
    --bg-base:        #0e1117;
    --bg-panel:       #161b22;
    --bg-card:        #1a2030;
    --bg-input:       #1e2430;
    --border:         #2a2f3a;
    --border-accent:  #2a3444;
    --green:          #7EB8A4;
    --green-dim:      #1a2e28;
    --green-border:   #2a4a3a;
    --text-primary:   #e8edf2;
    --text-secondary: #8a9ab0;
    --text-muted:     #5a6478;
    --gold:           #d4a843;
    --gold-bg:        #2a2210;
    --gold-border:    #3a3015;
    --silver:         #9ab0c8;
    --font-display:   'DM Serif Display', serif;
    --font-body:      'Lexend', sans-serif;
    --radius:         3px;
}

/* ── Reset Streamlit chrome ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer { display: none !important; }

/* Hide sidebar toggle */
[data-testid="collapsedControl"] { display: none; }

/* ── Top navigation bar ── */
.ss-topbar {
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    margin: -1rem -1rem 0 -1rem;
}
.ss-logo {
    font-family: var(--font-display);
    font-size: 22px;
    color: var(--green);
    letter-spacing: 0.5px;
}
.ss-logo span { color: #4ade98; }
.ss-nav { display: flex; gap: 6px; }
.ss-nav-btn {
    background: transparent;
    border: none;
    font-family: var(--font-body);
    font-size: 13px;
    font-weight: 500;
    color: var(--text-muted);
    padding: 6px 14px;
    border-radius: var(--radius);
    cursor: pointer;
    letter-spacing: 0.03em;
    transition: color 0.15s, background 0.15s;
}
.ss-nav-btn:hover { color: var(--text-primary); background: var(--bg-card); }
.ss-nav-btn.active { color: var(--green); background: var(--green-dim); }

/* ── Hero section ── */
.ss-hero {
    padding: 56px 0 40px;
    text-align: center;
}
.ss-hero-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 18px;
}
.ss-hero-title {
    font-family: var(--font-display);
    font-size: 48px;
    color: var(--text-primary);
    line-height: 1.1;
    margin-bottom: 16px;
}
.ss-hero-title span { color: var(--green); }
.ss-hero-sub {
    font-size: 16px;
    font-weight: 300;
    color: var(--text-secondary);
    max-width: 560px;
    margin: 0 auto 36px;
    line-height: 1.6;
}

/* ── Search bar ── */
.ss-searchbar-wrap {
    max-width: 680px;
    margin: 0 auto;
    position: relative;
}
/* Override Streamlit text_input */
[data-testid="stTextInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    height: 52px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(126,184,164,0.15) !important;
}
[data-testid="stTextInput"] label { color: var(--text-muted) !important; }

/* ── Filter chips ── */
.ss-filter-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 14px;
}
.ss-filter-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-right: 4px;
}
.ss-chip {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 2px;
    border: 1px solid var(--border-accent);
    color: var(--text-muted);
    background: transparent;
    cursor: pointer;
    font-family: var(--font-body);
    transition: all 0.1s;
}
.ss-chip.active {
    background: var(--green-dim);
    border-color: var(--green);
    color: var(--green);
}

/* ── Answer card ── */
.ss-answer-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 24px;
    margin-bottom: 20px;
}
.ss-answer-eyebrow {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 12px;
}
.ss-answer-text {
    font-size: 15px;
    font-weight: 300;
    line-height: 1.75;
    color: #c8d0dc;
}
.ss-cite {
    display: inline-block;
    background: var(--green-dim);
    border: 1px solid var(--green-border);
    border-radius: 2px;
    padding: 1px 6px;
    font-size: 11px;
    color: var(--green);
    font-weight: 600;
    vertical-align: middle;
    margin-left: 2px;
}

/* ── Source list ── */
.ss-sources-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 18px 0 10px;
}
.ss-source-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius);
    margin-bottom: 7px;
    transition: border-color 0.1s;
}
.ss-source-row:hover { border-color: var(--green); }
.ss-source-num {
    font-size: 12px;
    font-weight: 600;
    color: var(--green);
    min-width: 20px;
}
.ss-source-team {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}
.ss-source-meta {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 2px;
}
.ss-source-link {
    font-size: 12px;
    color: var(--green);
    text-decoration: none;
    margin-left: auto;
    white-space: nowrap;
    flex-shrink: 0;
}
.ss-source-link:hover { text-decoration: underline; }
.medal-gold {
    font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 2px;
    background: var(--gold-bg); color: var(--gold);
    border: 1px solid var(--gold-border);
    white-space: nowrap;
}
.medal-silver {
    font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 2px;
    background: #1e2228; color: var(--silver);
    border: 1px solid #2a3040;
    white-space: nowrap;
}
.medal-grand {
    font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 2px;
    background: #1a2028; color: var(--green);
    border: 1px solid #2a3840;
    white-space: nowrap;
}

/* ── Similar projects grid ── */
.ss-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 28px 0 14px;
}
.ss-section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}
.ss-section-badge {
    font-size: 10px;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 2px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text-muted);
}
.ss-similar-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.ss-similar-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    transition: border-color 0.1s;
}
.ss-similar-card:hover { border-color: #3a4a5a; }
.ss-sim-score {
    font-size: 11px; font-weight: 600;
    color: var(--green); margin-bottom: 5px;
}
.ss-sim-team {
    font-size: 14px; font-weight: 500;
    color: var(--text-primary); margin-bottom: 4px;
}
.ss-sim-title {
    font-size: 12px; color: var(--text-muted);
    line-height: 1.4; margin-bottom: 8px;
}
.ss-sim-tags { display: flex; gap: 5px; flex-wrap: wrap; }
.ss-sim-tag {
    font-size: 10px; font-weight: 500;
    padding: 2px 7px; border-radius: 2px;
    background: var(--bg-card); color: #6a7a90;
    border: 1px solid var(--border-accent);
}
.ss-score-bar {
    height: 2px; background: var(--border);
    border-radius: 1px; margin-top: 10px; overflow: hidden;
}
.ss-score-fill { height: 100%; background: var(--green); border-radius: 1px; }

/* ── Benchmark page ── */
.ss-bench-card {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    margin-bottom: 12px;
}
.ss-bench-system {
    font-size: 13px; font-weight: 600;
    color: var(--text-primary); margin-bottom: 4px;
}
.ss-bench-desc {
    font-size: 12px; color: var(--text-muted); margin-bottom: 14px;
}
.ss-metric-row { display: flex; gap: 12px; }
.ss-metric {
    flex: 1; background: var(--bg-card);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius);
    padding: 12px;
}
.ss-metric-name {
    font-size: 10px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 6px;
}
.ss-metric-val {
    font-size: 24px; font-weight: 600;
    color: var(--text-primary);
}
.ss-metric-bar-bg {
    height: 3px; background: var(--border);
    border-radius: 2px; margin-top: 8px; overflow: hidden;
}
.ss-metric-bar { height: 100%; border-radius: 2px; }

/* ── About page ── */
.ss-about-section {
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 24px;
    margin-bottom: 14px;
}
.ss-about-title {
    font-size: 14px; font-weight: 600;
    color: var(--text-primary); margin-bottom: 10px;
}
.ss-about-body {
    font-size: 13px; font-weight: 300;
    color: var(--text-secondary); line-height: 1.7;
}
.ss-about-body a { color: var(--green); text-decoration: none; }
.ss-about-body a:hover { text-decoration: underline; }
.ss-about-list {
    font-size: 13px; font-weight: 300;
    color: var(--text-secondary); line-height: 1.9;
    padding-left: 18px;
}
.ss-empty {
    text-align: center; padding: 48px 24px;
    color: var(--text-muted); font-size: 14px; font-weight: 300;
}
.ss-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 28px 0;
}

/* ── Streamlit button overrides ── */
[data-testid="baseButton-primary"] > button,
.stButton > button {
    background: var(--green) !important;
    color: #0e1117 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    padding: 10px 20px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Selectbox / multiselect overrides ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: var(--bg-input) !important;
    border-color: var(--border-accent) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--green) !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO DATA — replace these with real retrieval calls once index is built
# ═══════════════════════════════════════════════════════════════════════════════

DEMO_ANSWER = """
Toggle switches were used across multiple iGEM projects to create bistable
genetic circuits with two stable expression states. The most common design used
two mutually repressing promoters: when repressor A is active it silences gene B,
and vice versa <span class='ss-cite'>[1]</span>. Teams typically modelled
bistability in COPASI or Tellurium before cloning, checking that the nullcline
intersection produced two stable fixed points <span class='ss-cite'>[2]</span>.
Heidelberg 2021 implemented a toggle in <em>E. coli</em> using TetR and LacI as
the repressor pair, achieving a switching ratio of approximately 15-fold between
states <span class='ss-cite'>[3]</span>.
"""

DEMO_SOURCES = [
    {"num": 1, "team": "Heidelberg 2021", "track": "Foundational Advance",
     "year": 2021, "medal": "Grand Prize",
     "url": "https://2021.igem.org/Team:Heidelberg"},
    {"num": 2, "team": "Munich 2019", "track": "Foundational Advance",
     "year": 2019, "medal": "Gold",
     "url": "https://2019.igem.org/Team:Munich"},
    {"num": 3, "team": "ETH Zurich 2019", "track": "Foundational Advance",
     "year": 2019, "medal": "Gold",
     "url": "https://2019.igem.org/Team:ETH_Zurich"},
]

DEMO_SIMILAR = [
    {"score": 94, "team": "Heidelberg 2021", "year": 2021,
     "title": "Bistable toggle switch using TetR / LacI mutual repression",
     "track": "Foundational", "medal": "Grand Prize",
     "url": "https://2021.igem.org/Team:Heidelberg"},
    {"score": 87, "team": "ETH Zurich 2019", "year": 2019,
     "title": "Logic gate genetic circuit with bistable memory element",
     "track": "Foundational", "medal": "Gold",
     "url": "https://2019.igem.org/Team:ETH_Zurich"},
    {"score": 81, "team": "Marburg 2019", "year": 2019,
     "title": "Transcriptional toggle in Vibrio natriegens chassis",
     "track": "Foundational", "medal": "Gold",
     "url": "https://2019.igem.org/Team:Marburg"},
    {"score": 74, "team": "Imperial 2016", "year": 2016,
     "title": "Threshold biosensor with bistable output via RBS tuning",
     "track": "Diagnostics", "medal": "Silver",
     "url": "https://2016.igem.org/Team:Imperial_College"},
]

DEMO_BENCHMARK = [
    {"system": "Bare GPT-4o", "desc": "No retrieval — model answers from training data only",
     "faithfulness": 0.41, "relevancy": 0.58, "recall": 0.29, "color": "#E24B4A"},
    {"system": "GPT-4o + SynSearch RAG", "desc": "GPT-4o generation grounded in our iGEM corpus",
     "faithfulness": 0.79, "relevancy": 0.83, "recall": 0.71, "color": "#d4a843"},
    {"system": "Open model + SynSearch RAG", "desc": "DeepSeek-R1 distilled · fully open-source pipeline",
     "faithfulness": 0.74, "relevancy": 0.77, "recall": 0.68, "color": "#7EB8A4"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE — active page
# ═══════════════════════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "search"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def medal_badge(medal: str) -> str:
    """Return HTML badge for a medal string."""
    m = medal.strip().lower()
    if "grand" in m:
        return f"<span class='medal-grand'>{medal}</span>"
    elif "gold" in m:
        return f"<span class='medal-gold'>{medal}</span>"
    else:
        return f"<span class='medal-silver'>{medal}</span>"

def score_bar(pct: int, color: str = "#7EB8A4") -> str:
    return f"""
    <div class='ss-score-bar'>
      <div class='ss-score-fill' style='width:{pct}%; background:{color};'></div>
    </div>"""

def metric_bar(val: float, color: str) -> str:
    pct = int(val * 100)
    return f"""
    <div class='ss-metric-bar-bg'>
      <div class='ss-metric-bar' style='width:{pct}%; background:{color};'></div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# TOP NAV
# ═══════════════════════════════════════════════════════════════════════════════

def nav_button(label: str, page_key: str):
    active_class = "active" if st.session_state.page == page_key else ""
    if st.button(label, key=f"nav_{page_key}"):
        st.session_state.page = page_key
        st.rerun()

pages = [("Search", "search"), ("Similar projects", "similar"),
         ("Benchmark", "benchmark"), ("About", "about")]

nav_html = "<div class='ss-topbar'>"
nav_html += "<div class='ss-logo'>Syn<span>Search</span></div>"
nav_html += "<div class='ss-nav'>"
for label, key in pages:
    active = "active" if st.session_state.page == key else ""
    nav_html += f"<span class='ss-nav-btn {active}'>{label}</span>"
nav_html += "</div></div>"
st.markdown(nav_html, unsafe_allow_html=True)

# Invisible Streamlit buttons that actually handle clicks
nav_cols = st.columns(len(pages))
for i, (label, key) in enumerate(pages):
    with nav_cols[i]:
        if st.button(label, key=f"navbtn_{key}"):
            st.session_state.page = key
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.page == "search":

    # Hero
    st.markdown("""
    <div class='ss-hero'>
      <div class='ss-hero-eyebrow'>iGEM Knowledge Retrieval · 343 team wikis · 2019</div>
      <div class='ss-hero-title'>Ask the iGEM<br><span>archive</span></div>
      <div class='ss-hero-sub'>
        Search past iGEM team wikis with plain English. Every answer links
        directly to the original wiki page so you can verify the source.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Search input
    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        query = st.text_input(
            "Search query",
            placeholder="e.g.  How did teams detect heavy metals using biosensors?",
            label_visibility="collapsed",
            key="search_query",
        )

        # Filter row
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            year_filter = st.selectbox(
                "Year", ["All years", "2019", "2020", "2021", "2022"],
                label_visibility="visible", key="f_year"
            )
        with fcol2:
            track_filter = st.selectbox(
                "Track",
                ["All tracks", "Diagnostics", "Environment",
                 "Foundational Advance", "Manufacturing", "Food & Nutrition"],
                label_visibility="visible", key="f_track"
            )
        with fcol3:
            medal_filter = st.selectbox(
                "Medal", ["Any medal", "Grand Prize", "Gold", "Silver"],
                label_visibility="visible", key="f_medal"
            )

        search_btn = st.button("Search corpus", key="search_go", use_container_width=True)

    st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)

    # Results
    if query or search_btn:
        # ── In production: replace this block with your real retrieval call ──
        # from retrieval import search, find_similar
        # answer, sources = search(query, year=year_filter, track=track_filter, medal=medal_filter)
        # similar = find_similar(query, k=4)

        with st.spinner("Searching corpus..."):
            import time; time.sleep(0.6)   # remove when wiring real backend

        answer = DEMO_ANSWER
        sources = DEMO_SOURCES
        similar = DEMO_SIMILAR

        # Answer card — build sources HTML separately to avoid nested quote issues
        sources_html = ""
        for s in sources:
            badge = medal_badge(s["medal"])
            short_url = s["url"].replace("https://", "")
            sources_html += (
                f"<a href='{s['url']}' target='_blank' style='text-decoration:none;'>"
                f"<div class='ss-source-row'>"
                f"<div class='ss-source-num'>[{s['num']}]</div>"
                f"<div style='flex:1'>"
                f"<div class='ss-source-team'>{s['team']}</div>"
                f"<div class='ss-source-meta'>{s['track']} · {short_url}</div>"
                f"</div>{badge}</div></a>"
            )

        st.markdown(
            f"<div class='ss-answer-card'>"
            f"<div class='ss-answer-eyebrow'>Synthesised answer · {len(sources)} sources</div>"
            f"<div class='ss-answer-text'>{answer}</div>"
            f"<div class='ss-sources-label'>Sources — click to open original wiki</div>"
            f"{sources_html}</div>",
            unsafe_allow_html=True,
        )

        # Similar projects
        st.markdown("""
        <div class='ss-section-header'>
          <span class='ss-section-title'>Similar projects</span>
          <span class='ss-section-badge'>unique to SynSearch</span>
        </div>
        """, unsafe_allow_html=True)

        sim_html = "<div class='ss-similar-grid'>"
        for s in similar:
            sim_html += f"""
            <a href="{s['url']}" target="_blank" style="text-decoration:none;">
              <div class='ss-similar-card'>
                <div class='ss-sim-score'>{s['score']}% match</div>
                <div class='ss-sim-team'>{s['team']}</div>
                <div class='ss-sim-title'>{s['title']}</div>
                <div class='ss-sim-tags'>
                  <span class='ss-sim-tag'>{s['track']}</span>
                  <span class='ss-sim-tag'>{s['medal']}</span>
                  <span class='ss-sim-tag'>{s['year']}</span>
                </div>
                {score_bar(s['score'])}
              </div>
            </a>"""
        sim_html += "</div>"
        st.markdown(sim_html, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class='ss-empty'>
          Type a question above to search 343 iGEM team wikis.<br>
          Try: <em>"biosensor for heavy metal detection"</em> or
          <em>"genetic toggle switch in E. coli"</em>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SIMILAR PROJECTS
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "similar":

    st.markdown("""
    <div style='padding: 36px 0 28px;'>
      <div class='ss-hero-eyebrow'>Semantic similarity explorer</div>
      <div class='ss-hero-title' style='font-size:36px; text-align:left;'>
        Find projects like yours
      </div>
      <div class='ss-about-body' style='margin-top:10px; max-width:580px;'>
        Describe your project in plain English and SynSearch will surface the
        most semantically similar past iGEM teams — ranked by vector similarity,
        filterable by track and medal. Google can't do this.
      </div>
    </div>
    """, unsafe_allow_html=True)

    sim_query = st.text_input(
        "Describe your project",
        placeholder="e.g.  We're engineering E. coli to detect and report arsenic in water",
        key="sim_query"
    )
    sim_btn = st.button("Find similar projects", key="sim_go")

    if sim_query or sim_btn:
        with st.spinner("Computing similarity..."):
            import time; time.sleep(0.5)

        st.markdown("""
        <div class='ss-section-header' style='margin-top:24px;'>
          <span class='ss-section-title'>Top matches across 343 teams</span>
        </div>
        """, unsafe_allow_html=True)

        for s in DEMO_SIMILAR:
            st.markdown(f"""
            <a href="{s['url']}" target="_blank" style="text-decoration:none;">
              <div class='ss-bench-card' style='margin-bottom:10px;'>
                <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;'>
                  <div class='ss-source-team'>{s['team']}</div>
                  {medal_badge(s['medal'])}
                </div>
                <div class='ss-sim-title' style='font-size:13px; margin-bottom:8px;'>{s['title']}</div>
                <div style='display:flex; align-items:center; gap:16px;'>
                  <div class='ss-sim-tags'>
                    <span class='ss-sim-tag'>{s['track']}</span>
                    <span class='ss-sim-tag'>{s['year']}</span>
                  </div>
                  <div style='flex:1;'>
                    {score_bar(s['score'])}
                  </div>
                  <div class='ss-sim-score' style='white-space:nowrap;'>{s['score']}% match</div>
                </div>
              </div>
            </a>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BENCHMARK
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "benchmark":

    st.markdown("""
    <div style='padding: 36px 0 28px;'>
      <div class='ss-hero-eyebrow'>RAGAS evaluation · 50 ground-truth questions</div>
      <div class='ss-hero-title' style='font-size:36px; text-align:left;'>
        Does RAG actually help?
      </div>
      <div class='ss-about-body' style='margin-top:10px; max-width:600px;'>
        We compared three systems on the same 50 iGEM-specific questions with
        known answers. Scores are RAGAS metrics: faithfulness (did the answer
        stick to the sources?), answer relevancy, and context recall.
        <br><br>
        <strong style='color: #e8edf2;'>Result: RAG reduces hallucination by ~38 points on faithfulness.</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='ss-divider'>", unsafe_allow_html=True)

    for b in DEMO_BENCHMARK:
        st.markdown(f"""
        <div class='ss-bench-card'>
          <div class='ss-bench-system'>{b['system']}</div>
          <div class='ss-bench-desc'>{b['desc']}</div>
          <div class='ss-metric-row'>
            <div class='ss-metric'>
              <div class='ss-metric-name'>Faithfulness</div>
              <div class='ss-metric-val'>{b['faithfulness']:.2f}</div>
              {metric_bar(b['faithfulness'], b['color'])}
            </div>
            <div class='ss-metric'>
              <div class='ss-metric-name'>Answer relevancy</div>
              <div class='ss-metric-val'>{b['relevancy']:.2f}</div>
              {metric_bar(b['relevancy'], b['color'])}
            </div>
            <div class='ss-metric'>
              <div class='ss-metric-name'>Context recall</div>
              <div class='ss-metric-val'>{b['recall']:.2f}</div>
              {metric_bar(b['recall'], b['color'])}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='ss-about-section' style='margin-top:20px;'>
      <div class='ss-about-title'>How we built the ground truth</div>
      <div class='ss-about-body'>
        50 questions were written by the team based on real queries a new iGEM
        member would ask. For each question, the correct answer and the expected
        source wikis were verified manually. The question set covers Diagnostics,
        Foundational Advance, Environment, and Manufacturing tracks, with a mix
        of Gold and Grand Prize winning projects to avoid medal bias.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "about":

    st.markdown("""
    <div style='padding: 36px 0 28px;'>
      <div class='ss-hero-eyebrow'>iGEM 2025 Software Track</div>
      <div class='ss-hero-title' style='font-size:36px; text-align:left;'>
        About SynSearch
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='ss-about-section'>
      <div class='ss-about-title'>What it is</div>
      <div class='ss-about-body'>
        SynSearch is an open-source RAG (Retrieval-Augmented Generation) system
        that makes the iGEM archive searchable in plain English. A wet-lab
        biologist can describe what their team is working on and immediately
        find the most relevant past projects, protocols, and design choices —
        with direct links to the original wiki pages for verification.
      </div>
    </div>

    <div class='ss-about-section'>
      <div class='ss-about-title'>What we built on top of Munich 2024</div>
      <div class='ss-about-body'>
        Munich 2024 (<a href='https://gitlab.igem.org/2024/software-tools/munich' target='_blank'>gitlab.igem.org</a>)
        demonstrated that RAG reduces hallucination on iGEM wiki data.
        We reuse their scraped 2019 corpus under CC BY 4.0 and attribute them
        throughout. On top of that foundation, we independently built:
        <ul class='ss-about-list'>
          <li>Inline source citations with direct links to the original wiki page —
              the feature Munich listed as future work and never shipped</li>
          <li>Metadata filtering by year, track, and medal before retrieval</li>
          <li>A "Similar Projects" explorer using vector similarity — not available
              in any iGEM registry or search engine</li>
          <li>A published three-way RAGAS benchmark comparing bare GPT-4o,
              GPT-4o + RAG, and our open-source pipeline</li>
          <li>A zero-install hosted interface — no Docker, no terminal, no API key
              required from the user</li>
        </ul>
      </div>
    </div>

    <div class='ss-about-section'>
      <div class='ss-about-title'>Tech stack</div>
      <div class='ss-about-body'>
        sentence-transformers (embedding) · Chroma (vector store) ·
        Ollama / DeepSeek-R1 distilled (generation) · RAGAS (evaluation) ·
        Streamlit (interface) · Munich 2024 corpus (CC BY 4.0, attributed)
      </div>
    </div>

    <div class='ss-about-section'>
      <div class='ss-about-title'>Data attribution</div>
      <div class='ss-about-body'>
        The 2019 iGEM wiki corpus was scraped and pre-processed by the
        <a href='https://gitlab.igem.org/2024/software-tools/munich' target='_blank'>Munich 2024 iGEM team</a>
        and is used here under a Creative Commons Attribution 4.0
        International licence. We are grateful for their work.
      </div>
    </div>
    """, unsafe_allow_html=True)
