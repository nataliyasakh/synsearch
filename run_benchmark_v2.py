"""
run_benchmark_v2.py — SynSearch RAGAS benchmark, Groq-only.
Fixed RAGAS 0.1.21 judge configuration.
"""
import os, json, csv, time, tomllib
from pathlib import Path

with open(Path(".streamlit/secrets.toml"), "rb") as f:
    secrets = tomllib.load(f)

os.environ["PINECONE_API_KEY"] = secrets["PINECONE_API_KEY"]
os.environ["GROQ_API_KEY"]     = secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_KEY"]   = secrets["GROQ_API_KEY"]
os.environ["OPENAI_API_BASE"]  = "https://api.groq.com/openai/v1"

import pandas as pd
from groq import Groq
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from datasets import Dataset
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from ragas.llms import LangchainLLMWrapper

# ── Clients ───────────────────────────────────────────────────────────────────
groq_client = Groq(api_key=secrets["GROQ_API_KEY"])
embedder    = SentenceTransformer("all-MiniLM-L6-v2")
index       = Pinecone(api_key=secrets["PINECONE_API_KEY"]).Index("synsearch")

judge = LangchainLLMWrapper(ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_key=secrets["GROQ_API_KEY"],
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0,
))

MODEL_FAST  = "openai/gpt-oss-20b"
MODEL_LARGE = "qwen/qwen3.6-27b"

df            = pd.read_csv("benchmark_questions.csv")
questions     = df["question"].tolist()
ground_truths = df["expected_answer"].tolist()
print(f"Loaded {len(questions)} questions\n")

# ── Helpers ───────────────────────────────────────────────────────────────────
def retrieve(query):
    q_vec = embedder.encode([query], normalize_embeddings=True)[0].tolist()
    res = index.query(vector=q_vec, top_k=5, include_metadata=True)
    return [m.metadata.get("text", m.metadata.get("title",""))[:600]
            for m in res.matches]

def call_groq(model, system, user, retries=3):
    for attempt in range(retries):
        try:
            r = groq_client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":system},
                          {"role":"user","content":user}],
                temperature=0.1, max_tokens=300,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries-1:
                wait = 25*(attempt+1)
                print(f"    retry {attempt+1} in {wait}s ({type(e).__name__})")
                time.sleep(wait)
            else:
                print(f"    gave up: {e}")
                return ""

SYS_BARE = "You are a synthetic biology expert. Answer concisely in 2-4 sentences."
SYS_RAG  = ("You are a synthetic biology assistant. Answer using ONLY the provided "
            "context. Be concise (2-4 sentences). Say so if context lacks the answer.")

# ── Collect answers ───────────────────────────────────────────────────────────
rows_a, rows_b, rows_c = [], [], []
print("Collecting answers (15-20 min)...\n")

for i,(q,gt) in enumerate(zip(questions,ground_truths),1):
    print(f"[{i:02d}/50] {q[:65]}...")
    ctx = retrieve(q)

    ans_a = call_groq(MODEL_FAST, SYS_BARE, q)
    rows_a.append({"question":q,"answer":ans_a,
                   "contexts":["no retrieval"],"ground_truth":gt})
    time.sleep(2)

    ans_b = call_groq(MODEL_FAST, SYS_RAG,
                      f"Context:\n{chr(10).join(ctx)}\n\nQuestion: {q}")
    rows_b.append({"question":q,"answer":ans_b,
                   "contexts":ctx,"ground_truth":gt})
    time.sleep(2)

    ans_c = call_groq(MODEL_LARGE, SYS_RAG,
                      f"Context:\n{chr(10).join(ctx)}\n\nQuestion: {q}")
    rows_c.append({"question":q,"answer":ans_c,
                   "contexts":ctx,"ground_truth":gt})
    time.sleep(3)

# Save answers so we never lose them again
with open("benchmark_results.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["question","ground_truth","answer_a","answer_b","answer_c"])
    for a,b,c in zip(rows_a,rows_b,rows_c):
        w.writerow([a["question"],a["ground_truth"],
                    a["answer"],b["answer"],c["answer"]])
print("\nAnswers saved to benchmark_results.csv")

# ── RAGAS scoring ─────────────────────────────────────────────────────────────
print("\nScoring with RAGAS (Groq as judge)...")
print("This takes ~5 min. Progress bar will appear.\n")

# Set judge explicitly on each metric — required for ragas 0.1.21
f_metric  = faithfulness;      f_metric.llm  = judge
ar_metric = answer_relevancy;  ar_metric.llm = judge
cr_metric = context_recall;    cr_metric.llm = judge
metrics = [f_metric, ar_metric, cr_metric]

def score(rows, name):
    print(f"\nScoring: {name}")
    try:
        result = evaluate(Dataset.from_list(rows), metrics=metrics)
        s = {}
        for k in ["faithfulness","answer_relevancy","context_recall"]:
            try:
                s[k] = round(float(result[k]), 3)
            except:
                s[k] = 0.0
        print(f"  {s}")
        return s
    except Exception as e:
        print(f"  RAGAS error: {e}")
        return {"faithfulness":0.0,"answer_relevancy":0.0,"context_recall":0.0}

summary = {
    "Bare Groq (no retrieval)":   score(rows_a, "Bare Groq"),
    "Groq fast + SynSearch RAG":  score(rows_b, "Groq fast + RAG"),
    "Groq large + SynSearch RAG": score(rows_c, "Groq large + RAG"),
}

with open("benchmark_summary.json","w") as f:
    json.dump(summary, f, indent=2)

print("\n"+"="*55)
print("BENCHMARK RESULTS")
print("="*55)
for sys, s in summary.items():
    print(f"\n{sys}")
    for k,v in s.items():
        print(f"  {k}: {v:.3f}")
print("\nDone. Paste benchmark_summary.json into app.py Benchmark page.")
