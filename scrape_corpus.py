"""
scrape_corpus.py — iGEM wiki scraper for SynSearch.

Pre-2022:  team list from database.csv, scrapes year.igem.org/Team:Name
Post-2022: team list from api.igem.org, scrapes year.igem.wiki/name/page

Usage:
  python scrape_corpus.py --year 2019 --max_teams 50
  python scrape_corpus.py --year 2022 --max_teams 50
  python scrape_corpus.py --year 2023
"""

import json, time, argparse, requests, pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "SynSearch-iGEM2025-NYUAD (educational research)"}

parser = argparse.ArgumentParser()
parser.add_argument("--year",      type=int, required=True)
parser.add_argument("--max_teams", type=int, default=9999)
parser.add_argument("--delay",     type=float, default=1.0)
args = parser.parse_args()

OUT_DIR = Path(f"corpus_raw/{args.year}")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Competition UUIDs (cached to avoid extra API call) ────────────────────────
COMP_UUIDS = {}

def get_competition_uuid(year):
    if year in COMP_UUIDS:
        return COMP_UUIDS[year]
    r = requests.get(f"https://api.igem.org/v1/competitions/{year}/igem",
                     headers=HEADERS, timeout=20)
    if r.status_code == 200:
        uuid = r.json()["uuid"]
        COMP_UUIDS[year] = uuid
        return uuid
    return None

# ── PRE-2022: team list from database.csv ─────────────────────────────────────
def get_teams_pre2022(year):
    df = pd.read_csv("database.csv")
    df.columns = [c.strip() for c in df.columns]
    year_col  = next(c for c in df.columns if "year"  in c.lower())
    team_col  = next((c for c in df.columns if "team" in c.lower() and "name" in c.lower()),
                     next(c for c in df.columns if "team" in c.lower()))
    wiki_col  = next(c for c in df.columns if "wiki"  in c.lower())
    track_col = next(c for c in df.columns if "track" in c.lower())
    medal_col = next(c for c in df.columns if "medal" in c.lower())
    sub = df[pd.to_numeric(df[year_col], errors="coerce") == year].dropna(subset=[wiki_col])
    return [{"team": str(r[team_col]), "year": year,
             "track": str(r[track_col]), "medal": str(r[medal_col]),
             "wiki": str(r[wiki_col]).rstrip("/")}
            for _, r in sub.head(args.max_teams).iterrows()]

# ── POST-2022: team list from api.igem.org ────────────────────────────────────
def get_teams_post2022(year):
    uuid = get_competition_uuid(year)
    if not uuid:
        print(f"Could not get UUID for {year}")
        return []

    print(f"  Competition UUID: {uuid}")
    # Paginate through all teams
    teams = []
    page  = 1
    while len(teams) < args.max_teams:
        r = requests.get(
            f"https://api.igem.org/v1/competitions/{uuid}/teams",
            headers=HEADERS,
            params={"page": page},
            timeout=30)
        if r.status_code != 200:
            print(f"  Teams API failed: {r.status_code}")
            break
        raw  = r.json()
        data = raw.get("data", raw if isinstance(raw, list) else [])
        if not data:
            break
        for t in data:
            name = t.get("name", "")
            if not name:
                continue
            wiki_name = name.lower().replace("_", "-").replace(" ", "-")
            teams.append({
                "team":  name,
                "year":  year,
                "track": t.get("villageUUID", "Unknown"),
                "medal": "Unknown",
                "wiki":  f"https://{year}.igem.wiki/{wiki_name}",
            })
            if len(teams) >= args.max_teams:
                break
        if len(data) < 20:
            break
        page += 1
    return teams

# ── Page lists ────────────────────────────────────────────────────────────────
PAGES_PRE  = ["Description", "Design", "Results", "Experiments",
              "Model", "Safety", "Human_Practices", "Parts"]
PAGES_POST = ["description", "design", "results", "experiments",
              "model", "safety", "human-practices", "engineering",
              "notebook", "protocols"]

# ── Scrape one URL ────────────────────────────────────────────────────────────
def scrape_page(url, meta, page_name, source_type):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")

        if source_type == "mediawiki":
            content = (soup.find(id="mw-content-text") or
                       soup.find("div", {"class": "mw-content-ltr"}) or soup.body)
        else:
            content = (soup.find("main") or
                       soup.find(id="main-content") or
                       soup.find("article") or
                       soup.find("div", {"class": "content"}) or soup.body)

        if not content:
            return None
        for tag in content(["script","style","nav","footer","header","aside","noscript"]):
            tag.decompose()
        text = " ".join(content.get_text(separator=" ", strip=True).split())
        if len(text) < 150:
            return None
        return {"text": text,
                "metadata": {**meta, "url": url, "page": page_name, "source": source_type}}
    except Exception as e:
        return None

def save_record(record, team_dir):
    page = record["metadata"]["page"].replace("/","_").replace(" ","_")
    (team_dir / f"{page}.txt").write_text(record["text"], encoding="utf-8")
    (team_dir / f"{page}.meta.json").write_text(
        json.dumps(record["metadata"], indent=2), encoding="utf-8")

# ── MAIN ──────────────────────────────────────────────────────────────────────
print(f"\nScraping iGEM {args.year} (max {args.max_teams} teams)\n")

if args.year <= 2020:
    teams       = get_teams_pre2022(args.year)
    source_type = "mediawiki"
    pages       = PAGES_PRE
else:
    teams       = get_teams_post2022(args.year)
    source_type = "igem_wiki"
    pages       = PAGES_POST

print(f"Found {len(teams)} teams")
if not teams:
    print("No teams found.")
    exit(1)

print(f"First 3: {[t['team'] for t in teams[:3]]}\n")

total = 0
for i, t in enumerate(teams, 1):
    team_dir = OUT_DIR / t["team"].replace(" ","_").replace("/","_")
    team_dir.mkdir(exist_ok=True)
    meta = {"team": t["team"], "year": t["year"],
            "track": t["track"], "medal": t["medal"]}
    saved = 0
    for page in pages:
        url = f"{t['wiki']}/{page}"
        rec = scrape_page(url, meta, page, source_type)
        if rec:
            save_record(rec, team_dir)
            saved += 1
        time.sleep(args.delay)
    total += saved
    print(f"[{i:03d}/{len(teams)}] {t['team']}: {saved} pages")

print(f"\nDone. {total} pages saved to {OUT_DIR}/")
print(f"Next: python embed_corpus.py --year {args.year}")
