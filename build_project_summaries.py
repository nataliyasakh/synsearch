"""
build_project_summaries.py — one embedding per team -> Pinecone 'project-summaries' namespace
"""
import json, time, tomllib, re
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

with open(Path(".streamlit/secrets.toml"), "rb") as f:
    secrets = tomllib.load(f)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
pc    = Pinecone(api_key=secrets["PINECONE_API_KEY"])
index = pc.Index("synsearch")

NAMESPACE     = "project-summaries"
SUMMARY_WORDS = 600
BATCH_SIZE    = 100

VILLAGE_MAP = {
    "dd27c19e-d5a1-4b9e-9862-5a272dde6f23":"Agriculture",
    "e52aa171-f68b-4ec1-ac31-9a5a9b7975c1":"Art & Design",
    "776c19c2-de7d-4a1e-a0c3-a17708887721":"Biomanufacturing",
    "a770e27b-d43a-48c9-a066-5ea0893eff11":"Bioremediation",
    "78d23758-8754-4fbb-bbf0-e1e56119ab9d":"Climate Crisis",
    "1228b2cd-fb09-4035-bb1e-1d0d5e099877":"Conservation",
    "c318537d-0abc-4350-ae1b-d5b5a653819d":"Diagnostics",
    "6eedeb0f-7be5-4e60-84a8-6036548ca5fa":"Energy",
    "1e7c3c61-3a04-422f-82e6-d7c1f821cff6":"Environment",
    "fec79e23-8f03-467b-92ed-65a24c02877a":"Fashion & Cosmetics",
    "1967ad47-c93d-483c-b893-867d3070745f":"Food & Nutrition",
    "b62883b7-b186-465c-a381-f9dce17ddbcf":"Foundational Advance",
    "cedc951d-d1f3-4821-854d-1cd3e5b69f58":"Health & Medicine",
    "41007480-b7f7-4280-a995-8dee381ee316":"High School",
    "bb208fb6-063b-40ec-af0a-9a324c26f43a":"Infectious Diseases",
    "b3b30a28-16d2-454e-8ed2-cb405efc58b0":"Manufacturing",
    "74dee1c1-55d0-44eb-b8b7-6b55f6bd284b":"New Application",
    "d60d87c8-5303-459a-a5a2-79a33e0112be":"Oncology",
    "ccc0d43f-6a7e-4838-a751-afb408ae17fb":"Software & AI",
    "f18865a1-65a6-4112-9ad0-485fa50be8f8":"Space",
    "8cca60cf-f3b9-4f2a-aca3-b2c426461f88":"Therapeutics",
}

def clean(v):
    if v is None: return ""
    s = str(v).strip()
    return "" if s.lower() in ("none","nan","unknown","-") else s

def institution_name(team):
    return re.sub(r'\s*\d{4}\s*$', '', str(team)).strip() or str(team)

def truncate(text, max_words):
    return " ".join(str(text).split()[:max_words])

records = []

# 2019 from corpus.json
print("Loading 2019 from corpus.json...")
with open("corpus.json") as f:
    corpus = json.load(f)
for doc in corpus:
    records.append({
        "id":          "summary_" + str(doc["team"]).replace(" ","_") + "_2019",
        "text":        truncate(doc.get("text",""), SUMMARY_WORDS),
        "team":        clean(doc.get("team","")),
        "year":        2019,
        "institution": institution_name(doc.get("team","")),
        "track":       clean(doc.get("track","")),
        "medal":       clean(doc.get("prize","")),
        "url":         clean(doc.get("url","")),
        "title":       clean(doc.get("title","")),
        "pages":       "description",
    })
print(f"  {len(corpus)} teams from 2019")

# All other years from corpus_raw
for year_dir in sorted(Path("corpus_raw").iterdir()):
    if not year_dir.is_dir(): continue
    year = int(year_dir.name)
    count = 0
    for team_dir in sorted(year_dir.iterdir()):
        if not team_dir.is_dir(): continue
        texts, pages = [], []
        url = track = medal = ""
        for txt_file in sorted(team_dir.glob("*.txt")):
            txt = txt_file.read_text(encoding="utf-8", errors="ignore").strip()
            if txt:
                texts.append(txt)
                pages.append(txt_file.stem)
            meta_file = txt_file.with_suffix(".meta.json")
            if meta_file.exists() and not url:
                m = json.loads(meta_file.read_text())
                url   = clean(m.get("url",""))
                track = clean(VILLAGE_MAP.get(m.get("track",""), m.get("track","")))
                medal = clean(m.get("medal",""))
        if not texts: continue
        team_name = team_dir.name.replace("_"," ")
        records.append({
            "id":          "summary_" + team_dir.name + "_" + str(year),
            "text":        truncate(" ".join(texts), SUMMARY_WORDS),
            "team":        team_name,
            "year":        year,
            "institution": institution_name(team_name),
            "track":       track,
            "medal":       medal,
            "url":         url,
            "title":       "",
            "pages":       ",".join(pages),
        })
        count += 1
    print(f"  {count} teams from {year}")

print(f"\nTotal: {len(records)} summaries\n")

print("Embedding...")
vectors = model.encode(
    [r["text"] for r in records],
    batch_size=64, show_progress_bar=True, normalize_embeddings=True
)
print(f"Embedded {len(vectors)}")

print(f"Uploading to namespace '{NAMESPACE}'...")
for start in range(0, len(records), BATCH_SIZE):
    batch = records[start:start+BATCH_SIZE]
    vecs  = vectors[start:start+BATCH_SIZE]
    index.upsert(
        vectors=[{
            "id":     r["id"],
            "values": v.tolist(),
            "metadata": {
                "team":        r["team"],
                "year":        r["year"],
                "institution": r["institution"],
                "track":       r["track"],
                "medal":       r["medal"],
                "url":         r["url"],
                "title":       r["title"],
                "pages":       r["pages"],
            }
        } for r, v in zip(batch, vecs)],
        namespace=NAMESPACE
    )
    print(f"  {min(start+BATCH_SIZE, len(records))}/{len(records)}", end="\r")
    time.sleep(0.1)

print(f"\nDone. Stats: {index.describe_index_stats().namespaces}")
