"""
embed_corpus.py — reads corpus_raw/ folder and uploads to Pinecone.

Run after scrape_corpus.py:
  python embed_corpus.py --year 2022
  python embed_corpus.py --year 2023
  python embed_corpus.py  # embeds ALL years in corpus_raw/
"""

import os, json, time, argparse, tomllib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

with open(Path(".streamlit/secrets.toml"), "rb") as f:
    secrets = tomllib.load(f)

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, default=None)
parser.add_argument("--chunk_size", type=int, default=500)
parser.add_argument("--overlap",    type=float, default=0.15)
parser.add_argument("--batch_size", type=int, default=100)
args = parser.parse_args()

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
index = Pinecone(api_key=secrets["PINECONE_API_KEY"]).Index("synsearch")

def chunk_text(text, size=500, overlap=0.15):
    words = text.split()
    step  = max(1, int(size * (1 - overlap)))
    chunks = []
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        if piece:
            chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks

# Collect all .txt files
corpus_root = Path("corpus_raw")
if args.year:
    year_dirs = [corpus_root / str(args.year)]
else:
    year_dirs = sorted(corpus_root.iterdir())

all_records = []
for year_dir in year_dirs:
    if not year_dir.is_dir():
        continue
    year = year_dir.name
    for team_dir in sorted(year_dir.iterdir()):
        if not team_dir.is_dir():
            continue
        for txt_file in team_dir.glob("*.txt"):
            meta_file = txt_file.with_suffix(".meta.json")
            if not meta_file.exists():
                continue
            text = txt_file.read_text(encoding="utf-8")
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            for i, chunk in enumerate(chunk_text(text, args.chunk_size, args.overlap)):
                chunk_id = f"{meta['team'].replace(' ','_')}_{meta['year']}_{txt_file.stem}_{i}"
                all_records.append({
                    "id":     chunk_id,
                    "text":   chunk,
                    "meta":   meta,
                })

print(f"Found {len(all_records)} chunks to embed and upload")

# Embed in batches
texts   = [r["text"] for r in all_records]
vectors = model.encode(texts, batch_size=64, show_progress_bar=True,
                       normalize_embeddings=True)
print(f"Embedded {len(vectors)} chunks")

# Upload to Pinecone
print(f"Uploading in batches of {args.batch_size}...")
for start in range(0, len(all_records), args.batch_size):
    batch = all_records[start:start + args.batch_size]
    vecs  = vectors[start:start + args.batch_size]
    index.upsert(vectors=[
        {"id": r["id"], "values": v.tolist(), "metadata": {k: (v2 if v2 is not None else "") for k,v2 in r["meta"].items()}}
        for r, v in zip(batch, vecs)
    ])
    done = min(start + args.batch_size, len(all_records))
    print(f"  uploaded {done}/{len(all_records)}", end="\r")
    time.sleep(0.1)

print(f"\nDone. {len(all_records)} vectors uploaded to Pinecone.")
print(f"Index stats: {index.describe_index_stats()}")
