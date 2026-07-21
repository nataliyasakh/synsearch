"""
SynSearch — iGEM Knowledge Retrieval
Design: Dunelock system (NYUAD iGEM 2026) — warm basalt dark palette,
square corners, hairline borders, no shadows, no glassmorphism.
"""
import time
import streamlit as st

st.set_page_config(
    page_title="SynSearch",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');

/* ── Dunelock dark tokens ── */
:root {
  --maroon:  #6E1E18;
  --orange:  #D6884A;
  --teal:    #8FB3AC;
  --rose:    #C28A7C;
  --sand:    #E7D8C4;
  --paper:   #FBF7F0;
  --basalt:  #1a1512;
  --slate:   #241c19;
  --card:    #2e2622;
  --border:  #3d322c;
  --ash:     #8a7e75;
  --text:    #e8e0d8;
  --muted:   #6b5f57;
  --radius:  3px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--basalt) !important;
  font-family: 'Lexend', sans-serif !important;
  color: var(--text) !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], footer,
[data-testid="collapsedControl"] { display: none !important; }

/* ── NAV ── */
.nav {
  background: var(--slate);
  border-bottom: 1px solid var(--border);
  padding: 0 36px;
  display: flex; align-items: center; justify-content: space-between;
  height: 54px;
  margin: -1rem -1rem 0;
  position: sticky; top: 0; z-index: 100;
}
.nav-logo {
  font-size: 17px; font-weight: 700;
  letter-spacing: .06em; text-transform: uppercase;
  color: var(--orange);
}
.nav-logo span { color: var(--teal); font-weight: 300; }
.nav-links { display: flex; gap: 2px; }
.nav-link {
  font-size: 12px; font-weight: 500;
  letter-spacing: .04em;
  color: var(--ash); padding: 6px 13px;
  border-radius: var(--radius);
  cursor: pointer; border: none;
  background: transparent; font-family: 'Lexend', sans-serif;
  transition: color .12s, background .12s;
}
.nav-link:hover { color: var(--text); background: var(--card); }
.nav-link.active { color: var(--orange); background: #2e1e14; }

/* ── HERO ── */
.hero { padding: 64px 0 40px; text-align: center; }
.eyebrow {
  font-size: 10px; font-weight: 700;
  letter-spacing: .18em; text-transform: uppercase;
  color: var(--teal); margin-bottom: 18px;
}
.hero-title {
  font-size: 54px; font-weight: 700;
  line-height: 1.05; color: var(--text);
  margin-bottom: 18px; letter-spacing: -.01em;
}
.hero-title em { font-style: normal; color: var(--orange); }
.hero-sub {
  font-size: 15px; font-weight: 300;
  color: var(--ash); max-width: 500px;
  margin: 0 auto 36px; line-height: 1.7;
}

/* ── INPUT overrides ── */
[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Lexend', sans-serif !important;
  font-size: 14px !important;
  padding: 13px 16px !important;
  height: 48px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--orange) !important;
  box-shadow: none !important;
  outline: 2px solid var(--orange) !important;
  outline-offset: 0 !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* ── SELECTBOX overrides ── */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: 'Lexend', sans-serif !important;
  font-size: 13px !important;
}
[data-testid="stSelectbox"] label {
  font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  color: var(--muted) !important;
}

/* ── BUTTON override ── */
.stButton > button {
  background: var(--orange) !important;
  color: var(--basalt) !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-family: 'Lexend', sans-serif !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  letter-spacing: .04em !important;
  text-transform: uppercase !important;
  height: 46px !important;
  transition: opacity .12s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── DIVIDER ── */
.sep { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

/* ── ANSWER CARD ── */
.answer-card {
  background: var(--slate);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 26px;
  margin-bottom: 20px;
}
.card-eyebrow {
  font-size: 10px; font-weight: 700;
  letter-spacing: .15em; text-transform: uppercase;
  color: var(--teal); margin-bottom: 14px;
}
.answer-body {
  font-size: 14px; font-weight: 300;
  line-height: 1.85; color: #c8bfb4;
}
.cite-tag {
  display: inline-block;
  border: 1px solid var(--border);
  padding: 0px 6px;
  font-size: 10px; font-weight: 700;
  color: var(--teal);
  border-radius: var(--radius);
  vertical-align: middle; margin-left: 2px;
}
.sources-head {
  font-size: 10px; font-weight: 700;
  letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); margin: 20px 0 10px;
}
.source-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 6px;
  text-decoration: none;
  transition: border-color .12s;
}
.source-row:hover { border-color: var(--orange); }
.src-num { font-size: 11px; font-weight: 700; color: var(--teal); min-width: 22px; }
.src-info { flex: 1; }
.src-team { font-size: 13px; font-weight: 500; color: var(--text); }
.src-meta { font-size: 11px; color: var(--muted); margin-top: 2px; }
.badge {
  font-size: 10px; font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius);
  white-space: nowrap;
  border: 1px solid;
}
.badge-grand { color: var(--teal);   background: #16241f; border-color: #2a4038; }
.badge-gold  { color: var(--orange); background: #2a1a0c; border-color: #4a2e12; }
.badge-silver{ color: var(--ash);    background: var(--card); border-color: var(--border); }

/* ── SIMILAR GRID ── */
.section-head {
  display: flex; align-items: center; gap: 10px; margin: 28px 0 12px;
}
.section-title {
  font-size: 10px; font-weight: 700;
  letter-spacing: .15em; text-transform: uppercase;
  color: var(--muted);
}
.section-pill {
  font-size: 10px; font-weight: 600;
  padding: 2px 9px;
  border: 1px solid #2a4038;
  color: var(--teal); background: #16241f;
  border-radius: var(--radius);
}
.sim-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.sim-card {
  background: var(--slate); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
  text-decoration: none; display: block;
  transition: border-color .12s;
}
.sim-card:hover { border-color: var(--orange); }
.sim-pct { font-size: 11px; font-weight: 700; color: var(--teal); margin-bottom: 5px; }
.sim-team { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.sim-title-text { font-size: 12px; color: var(--ash); line-height: 1.4; margin-bottom: 8px; }
.tags { display: flex; gap: 5px; flex-wrap: wrap; }
.tag {
  font-size: 10px; font-weight: 500; padding: 2px 7px;
  border-radius: var(--radius);
  background: var(--card); color: var(--muted);
  border: 1px solid var(--border);
}
.score-bar { height: 2px; background: var(--border); border-radius: 1px; margin-top: 10px; overflow: hidden; }
.score-fill { height: 100%; background: var(--teal); border-radius: 1px; }

/* ── BENCHMARK ── */
.bench-card {
  background: var(--slate); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 22px 24px; margin-bottom: 10px;
}
.bench-name { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.bench-desc { font-size: 12px; color: var(--muted); margin-bottom: 16px; }
.metric-row { display: flex; gap: 10px; }
.metric {
  flex: 1; background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px;
}
.metric-label {
  font-size: 10px; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 6px;
}
.metric-val { font-size: 28px; font-weight: 700; color: var(--text); }
.mbar-bg { height: 2px; background: var(--border); border-radius: 1px; margin-top: 8px; overflow: hidden; }
.mbar { height: 100%; border-radius: 1px; }

/* ── ABOUT ── */
.about-card {
  background: var(--slate); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 22px 24px; margin-bottom: 10px;
}
.about-h { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 9px; }
.about-p { font-size: 13px; font-weight: 300; color: var(--ash); line-height: 1.75; }
.about-p a { color: var(--teal); text-decoration: none; }
.about-p a:hover { text-decoration: underline; }
.about-ul { font-size: 13px; font-weight: 300; color: var(--ash); line-height: 2; padding-left: 18px; }

.empty-state {
  text-align: center; padding: 60px 0;
  color: var(--muted); font-size: 14px; font-weight: 300;
}
</style>
""", unsafe_allow_html=True)

# ── DEMO DATA ──────────────────────────────────────────────────────────────────
DEMO_ANSWER = (
    "Toggle switches create bistable genetic circuits with two stable expression states. "
    "The most common design uses two mutually repressing promoters — when repressor A is "
    "active it silences gene B, and vice versa <span class='cite-tag'>[1]</span>. Teams "
    "typically modelled bistability in COPASI before cloning, checking that nullcline "
    "intersections produced two stable fixed points <span class='cite-tag'>[2]</span>. "
    "Heidelberg 2021 implemented a TetR/LacI toggle in <em>E. coli</em>, achieving a "
    "switching ratio of ~15-fold between states <span class='cite-tag'>[3]</span>."
)
DEMO_SOURCES = [
    {"num":1,"team":"Heidelberg 2021","track":"Foundational Advance","year":2021,
     "medal":"Grand Prize","url":"https://2021.igem.org/Team:Heidelberg"},
    {"num":2,"team":"Munich 2019","track":"Foundational Advance","year":2019,
     "medal":"Gold","url":"https://2019.igem.org/Team:Munich"},
    {"num":3,"team":"ETH Zurich 2019","track":"Foundational Advance","year":2019,
     "medal":"Gold","url":"https://2019.igem.org/Team:ETH_Zurich"},
]
DEMO_SIMILAR = [
    {"score":94,"team":"Heidelberg 2021","year":2021,
     "title":"Bistable toggle switch using TetR/LacI mutual repression",
     "track":"Foundational","medal":"Grand Prize","url":"https://2021.igem.org/Team:Heidelberg"},
    {"score":87,"team":"ETH Zurich 2019","year":2019,
     "title":"Logic gate genetic circuit with bistable memory element",
     "track":"Foundational","medal":"Gold","url":"https://2019.igem.org/Team:ETH_Zurich"},
    {"score":81,"team":"Marburg 2019","year":2019,
     "title":"Transcriptional toggle in Vibrio natriegens chassis",
     "track":"Foundational","medal":"Gold","url":"https://2019.igem.org/Team:Marburg"},
    {"score":74,"team":"Imperial 2016","year":2016,
     "title":"Threshold biosensor with bistable output via RBS tuning",
     "track":"Diagnostics","medal":"Silver","url":"https://2016.igem.org/Team:Imperial_College"},
]
DEMO_BENCH = [
    {"name":"Bare GPT-4o","desc":"No retrieval — model answers from training data only",
     "f":0.41,"r":0.58,"c":0.29,"color":"#6E1E18"},
    {"name":"GPT-4o + SynSearch RAG","desc":"GPT-4o generation grounded in our iGEM corpus",
     "f":0.79,"r":0.83,"c":0.71,"color":"#D6884A"},
    {"name":"Open model + SynSearch RAG","desc":"DeepSeek-R1 distilled · fully open-source pipeline",
     "f":0.74,"r":0.77,"c":0.68,"color":"#8FB3AC"},
]

# ── HELPERS ────────────────────────────────────────────────────────────────────
def badge(medal):
    m = medal.lower()
    if "grand" in m: return f"<span class='badge badge-grand'>{medal}</span>"
    if "gold"  in m: return f"<span class='badge badge-gold'>{medal}</span>"
    return f"<span class='badge badge-silver'>{medal}</span>"

def sbar(pct):
    return f"<div class='score-bar'><div class='score-fill' style='width:{pct}%'></div></div>"

def mbar(val, color):
    return f"<div class='mbar-bg'><div class='mbar' style='width:{int(val*100)}%;background:{color}'></div></div>"

# ── SESSION ────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "search"

# ── NAV ───────────────────────────────────────────────────────────────────────
PAGES = [("Search","search"),("Similar Projects","similar"),
         ("Benchmark","benchmark"),("About","about")]

nav_links = "".join(
    f"<span class='nav-link {'active' if st.session_state.page==k else ''}'>{l}</span>"
    for l,k in PAGES
)
st.markdown(
    f"<div class='nav'>"
    f"<div class='nav-logo'>Syn<span>Search</span></div>"
    f"<div class='nav-links'>{nav_links}</div>"
    f"</div>",
    unsafe_allow_html=True
)
nav_cols = st.columns(len(PAGES))
for i,(label,key) in enumerate(PAGES):
    with nav_cols[i]:
        if st.button(label, key=f"nb_{key}"):
            st.session_state.page = key
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "search":

    st.markdown("""
    <div class='hero'>
      <div class='eyebrow'>iGEM knowledge retrieval &middot; 343 wikis &middot; 2019 corpus</div>
      <div class='hero-title'>Ask the iGEM<br><em>archive</em></div>
      <div class='hero-sub'>
        Search past iGEM team wikis in plain English.
        Every answer links back to the original source so you can verify it.
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1,3,1])
    with mid:
        query = st.text_input("q", placeholder="e.g.  How did teams build biosensors for heavy metal detection?", label_visibility="collapsed", key="q")
        fc1, fc2, fc3 = st.columns(3)
        with fc1: year  = st.selectbox("Year",  ["All years","2019","2020","2021","2022"], key="fy")
        with fc2: track = st.selectbox("Track", ["All tracks","Diagnostics","Environment","Foundational Advance","Manufacturing"], key="ft")
        with fc3: medal = st.selectbox("Medal", ["Any medal","Grand Prize","Gold","Silver"], key="fm")
        go = st.button("Search corpus", key="go", use_container_width=True)

    st.markdown("<hr class='sep'>", unsafe_allow_html=True)

    if query or go:
        # ── swap with real_search(query, year, track, medal) when backend is ready ──
        with st.spinner("Searching corpus..."):
            time.sleep(0.4)
        answer  = DEMO_ANSWER
        sources = DEMO_SOURCES
        similar = DEMO_SIMILAR

        # sources HTML — built separately, no nested quote issues
        src_rows = ""
        for s in sources:
            short = s["url"].replace("https://","")
            src_rows += (
                f"<a href='{s['url']}' target='_blank' class='source-row'>"
                f"<div class='src-num'>[{s['num']}]</div>"
                f"<div class='src-info'>"
                f"<div class='src-team'>{s['team']}</div>"
                f"<div class='src-meta'>{s['track']} &middot; {short}</div>"
                f"</div>{badge(s['medal'])}</a>"
            )

        st.markdown(
            f"<div class='answer-card'>"
            f"<div class='card-eyebrow'>Synthesised answer &middot; {len(sources)} sources</div>"
            f"<div class='answer-body'>{answer}</div>"
            f"<div class='sources-head'>Sources — click to open original wiki</div>"
            f"{src_rows}</div>",
            unsafe_allow_html=True
        )

        # similar projects
        st.markdown(
            "<div class='section-head'>"
            "<span class='section-title'>Similar projects</span>"
            "<span class='section-pill'>unique to SynSearch</span>"
            "</div>",
            unsafe_allow_html=True
        )
        sim = "<div class='sim-grid'>"
        for s in similar:
            sim += (
                f"<a href='{s['url']}' target='_blank' class='sim-card'>"
                f"<div class='sim-pct'>{s['score']}% match</div>"
                f"<div class='sim-team'>{s['team']}</div>"
                f"<div class='sim-title-text'>{s['title']}</div>"
                f"<div class='tags'>"
                f"<span class='tag'>{s['track']}</span>"
                f"<span class='tag'>{s['medal']}</span>"
                f"<span class='tag'>{s['year']}</span>"
                f"</div>{sbar(s['score'])}</a>"
            )
        sim += "</div>"
        st.markdown(sim, unsafe_allow_html=True)

    else:
        st.markdown(
            "<div class='empty-state'>"
            "Type a question above and press Search corpus.<br>"
            "Try: <em>\"biosensor for heavy metal detection\"</em> &nbsp;or&nbsp; "
            "<em>\"genetic toggle switch in E. coli\"</em>"
            "</div>",
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# SIMILAR PROJECTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "similar":
    st.markdown("""
    <div style='padding:52px 0 28px'>
      <div class='eyebrow'>Semantic similarity explorer</div>
      <div class='hero-title' style='font-size:40px;text-align:left'>
        Find projects<br><em>like yours</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0'>
        Describe your project. SynSearch ranks the 343 closest past teams
        by vector similarity. Google cannot do this.
      </div>
    </div>
    """, unsafe_allow_html=True)

    sq = st.text_input("sq", placeholder="e.g.  We are engineering E. coli to detect arsenic in drinking water", label_visibility="collapsed", key="sq")
    if st.button("Find similar projects", key="sgo") or sq:
        with st.spinner("Computing similarity..."):
            time.sleep(0.4)
        st.markdown(
            "<div class='section-head' style='margin-top:24px'>"
            "<span class='section-title'>Top matches across 343 teams</span>"
            "</div>",
            unsafe_allow_html=True
        )
        for s in DEMO_SIMILAR:
            st.markdown(
                f"<a href='{s['url']}' target='_blank' class='source-row' style='margin-bottom:8px'>"
                f"<div class='src-info'>"
                f"<div class='src-team'>{s['team']} &middot; {s['year']}</div>"
                f"<div class='src-meta' style='margin-top:3px'>{s['title']}</div>"
                f"</div>"
                f"{badge(s['medal'])}"
                f"<div class='sim-pct' style='white-space:nowrap;margin-left:10px'>{s['score']}%</div>"
                f"</a>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# BENCHMARK
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "benchmark":
    st.markdown("""
    <div style='padding:52px 0 28px'>
      <div class='eyebrow'>RAGAS evaluation &middot; 50 ground-truth questions</div>
      <div class='hero-title' style='font-size:40px;text-align:left'>
        Does RAG<br><em>actually help?</em>
      </div>
      <div class='hero-sub' style='text-align:left;margin:12px 0 0'>
        Three systems, same 50 iGEM questions, verified answers.
        RAG reduces hallucination by ~38 points on faithfulness.
      </div>
    </div>
    <hr class='sep'>
    """, unsafe_allow_html=True)

    for b in DEMO_BENCH:
        st.markdown(
            f"<div class='bench-card'>"
            f"<div class='bench-name'>{b['name']}</div>"
            f"<div class='bench-desc'>{b['desc']}</div>"
            f"<div class='metric-row'>"
            f"<div class='metric'><div class='metric-label'>Faithfulness</div>"
            f"<div class='metric-val'>{b['f']:.2f}</div>{mbar(b['f'],b['color'])}</div>"
            f"<div class='metric'><div class='metric-label'>Answer relevancy</div>"
            f"<div class='metric-val'>{b['r']:.2f}</div>{mbar(b['r'],b['color'])}</div>"
            f"<div class='metric'><div class='metric-label'>Context recall</div>"
            f"<div class='metric-val'>{b['c']:.2f}</div>{mbar(b['c'],b['color'])}</div>"
            f"</div></div>",
            unsafe_allow_html=True
        )
    st.markdown("""
    <div class='about-card' style='margin-top:8px'>
      <div class='about-h'>How we built the ground truth</div>
      <div class='about-p'>
        50 questions based on real queries a new iGEM team member would ask,
        spanning Diagnostics, Foundational Advance, Environment, and Manufacturing tracks.
        Correct answers and source wikis were verified manually.
        <br><br><em style='color:#4a3f38'>Numbers above are placeholders — replace with real RAGAS output.</em>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":
    st.markdown("""
    <div style='padding:52px 0 28px'>
      <div class='eyebrow'>iGEM 2025 Software Track</div>
      <div class='hero-title' style='font-size:40px;text-align:left'>
        About<br><em>SynSearch</em>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='about-card'>
      <div class='about-h'>What it is</div>
      <div class='about-p'>
        SynSearch makes the iGEM archive searchable in plain English. Describe what your team
        is working on and instantly find the most relevant past projects, protocols, and design
        choices — with direct links to the original wiki pages for verification.
        No hallucinated citations. No terminal required.
      </div>
    </div>
    <div class='about-card'>
      <div class='about-h'>What we built beyond Munich 2024</div>
      <div class='about-p'>
        Munich 2024 proved RAG reduces hallucination on iGEM data. We reuse their
        scraped 2019 corpus under CC BY 4.0 and independently built:
        <ul class='about-ul'>
          <li>Inline source citations linking to the original wiki — Munich's own listed future work</li>
          <li>Metadata filtering by year, track, and medal before retrieval</li>
          <li>A "Similar Projects" semantic explorer not available in any registry</li>
          <li>Published three-way RAGAS benchmark: bare GPT-4o vs GPT-4o+RAG vs open model+RAG</li>
          <li>Zero-install hosted interface — no Docker, no terminal, no user API key required</li>
        </ul>
      </div>
    </div>
    <div class='about-card'>
      <div class='about-h'>Stack</div>
      <div class='about-p'>
        sentence-transformers &middot; Pinecone &middot; Groq API &middot;
        RAGAS &middot; Streamlit Cloud &middot; Munich 2024 corpus (CC BY 4.0)
      </div>
    </div>
    <div class='about-card'>
      <div class='about-h'>Data attribution</div>
      <div class='about-p'>
        The 2019 iGEM wiki corpus was scraped and curated by the
        <a href='https://gitlab.igem.org/2024/software-tools/munich' target='_blank'>Munich 2024 iGEM team</a>
        and is used under Creative Commons Attribution 4.0. We are grateful for their work.
      </div>
    </div>
    """, unsafe_allow_html=True)
