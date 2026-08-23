"""
rescore_fallbacks.py — re-scores only questions where all three scores are 0.5
(those are fallback values from failed judge calls when laptop slept).
Patches benchmark_scores_detail.csv and regenerates benchmark_summary.json.
"""

import os, json, time, tomllib, csv
from pathlib import Path
from groq import Groq
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import pandas as pd

with open(Path(".streamlit/secrets.toml"), "rb") as f:
    secrets = tomllib.load(f)

groq_client = Groq(api_key=secrets["GROQ_API_KEY"])
embedder    = SentenceTransformer("all-MiniLM-L6-v2")
index       = Pinecone(api_key=secrets["PINECONE_API_KEY"]).Index("synsearch")

JUDGE_MODEL = "openai/gpt-oss-20b"

def judge(prompt, retries=3):
    for attempt in range(retries):
        try:
            r = groq_client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0, max_tokens=500,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(20 * (attempt + 1))
            else:
                return "0.5"

def extract_score(text):
    import re
    matches = re.findall(r"0?\.\d+|[01]\.0*|[01]", text)
    for m in matches:
        try:
            v = float(m)
            if 0.0 <= v <= 1.0:
                return v
        except:
            pass
    return 0.5

def score_faithfulness(q, answer, contexts):
    ctx_str = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
    prompt = f"""You are an impartial judge. Score whether this answer is faithful to the source contexts.

Question: {q}
Answer: {answer}
Contexts:
{ctx_str}

Faithfulness score 0.0-1.0:
- 1.0 = every claim supported by contexts
- 0.5 = some claims supported
- 0.0 = answer contains information not in contexts

Reply with ONLY a decimal number."""
    return extract_score(judge(prompt))

def score_relevancy(q, answer):
    prompt = f"""You are an impartial judge. Score whether this answer addresses the question.

Question: {q}
Answer: {answer}

Relevancy score 0.0-1.0:
- 1.0 = directly and completely addresses the question
- 0.5 = partially addresses it
- 0.0 = off-topic

Reply with ONLY a decimal number."""
    return extract_score(judge(prompt))

def score_recall(q, answer, gt, contexts):
    ctx_str = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
    prompt = f"""You are an impartial judge. Score whether the retrieved contexts contain enough information to answer this question correctly.

Question: {q}
Correct answer: {gt}
Contexts:
{ctx_str}

Context recall score 0.0-1.0:
- 1.0 = contexts contain all needed information
- 0.5 = contexts contain some relevant information  
- 0.0 = contexts contain nothing useful

Reply with ONLY a decimal number."""
    return extract_score(judge(prompt))

def retrieve(query):
    q_vec = embedder.encode([query], normalize_embeddings=True)[0].tolist()
    res = index.query(vector=q_vec, top_k=5, include_metadata=True)
    return [m.metadata.get("text", m.metadata.get("title",""))[:500]
            for m in res.matches]

# ── Load both files ───────────────────────────────────────────────────────────
answers_df = pd.read_csv("benchmark_results.csv")
scores_df  = pd.read_csv("benchmark_scores_detail.csv")

# Identify fallback rows — where ALL scores for a system are 0.5
def is_fallback(row):
    for prefix in ["a_", "b_", "c_"]:
        vals = [row[f"{prefix}faith"], row[f"{prefix}rel"], row[f"{prefix}recall"]]
        if all(v == 0.5 for v in vals):
            return True
    return False

fallback_idx = [i for i, row in scores_df.iterrows() if is_fallback(row)]
print(f"Found {len(fallback_idx)} rows with fallback 0.5 scores")
print(f"Row indices: {fallback_idx}\n")

# ── Rescore fallback rows ─────────────────────────────────────────────────────
for count, idx in enumerate(fallback_idx, 1):
    q  = answers_df.loc[idx, "question"]
    gt = answers_df.loc[idx, "ground_truth"]
    ans_a = str(answers_df.loc[idx, "answer_a"])
    ans_b = str(answers_df.loc[idx, "answer_b"])
    ans_c = str(answers_df.loc[idx, "answer_c"])
    ctx = retrieve(q)

    print(f"[{count}/{len(fallback_idx)}] row {idx+1}: {q[:60]}...")

    # Only rescore the systems that have all-0.5
    row = scores_df.loc[idx]

    if all(row[k] == 0.5 for k in ["a_faith","a_rel","a_recall"]):
        fa = score_faithfulness(q, ans_a, ["no retrieval context"])
        ra = score_relevancy(q, ans_a)
        ca = score_recall(q, ans_a, gt, ["no retrieval context"])
        scores_df.loc[idx, ["a_faith","a_rel","a_recall"]] = [fa, ra, ca]
        time.sleep(2)
    
    if all(row[k] == 0.5 for k in ["b_faith","b_rel","b_recall"]):
        fb = score_faithfulness(q, ans_b, ctx)
        rb = score_relevancy(q, ans_b)
        cb = score_recall(q, ans_b, gt, ctx)
        scores_df.loc[idx, ["b_faith","b_rel","b_recall"]] = [fb, rb, cb]
        time.sleep(2)

    if all(row[k] == 0.5 for k in ["c_faith","c_rel","c_recall"]):
        fc = score_faithfulness(q, ans_c, ctx)
        rc = score_relevancy(q, ans_c)
        cc = score_recall(q, ans_c, gt, ctx)
        scores_df.loc[idx, ["c_faith","c_rel","c_recall"]] = [fc, rc, cc]
        time.sleep(3)

    print(f"  A({scores_df.loc[idx,'a_faith']:.2f}/{scores_df.loc[idx,'a_rel']:.2f}/{scores_df.loc[idx,'a_recall']:.2f}) "
          f"B({scores_df.loc[idx,'b_faith']:.2f}/{scores_df.loc[idx,'b_rel']:.2f}/{scores_df.loc[idx,'b_recall']:.2f}) "
          f"C({scores_df.loc[idx,'c_faith']:.2f}/{scores_df.loc[idx,'c_rel']:.2f}/{scores_df.loc[idx,'c_recall']:.2f})")

# ── Save updated scores ───────────────────────────────────────────────────────
scores_df.to_csv("benchmark_scores_detail.csv", index=False)

# ── Regenerate summary ────────────────────────────────────────────────────────
def avg(col): return round(float(scores_df[col].mean()), 3)

summary = {
    "Bare Groq (no retrieval)": {
        "faithfulness":     avg("a_faith"),
        "answer_relevancy": avg("a_rel"),
        "context_recall":   avg("a_recall"),
    },
    "Groq fast + SynSearch RAG": {
        "faithfulness":     avg("b_faith"),
        "answer_relevancy": avg("b_rel"),
        "context_recall":   avg("b_recall"),
    },
    "Groq large + SynSearch RAG": {
        "faithfulness":     avg("c_faith"),
        "answer_relevancy": avg("c_rel"),
        "context_recall":   avg("c_recall"),
    },
}

with open("benchmark_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "="*55)
print("UPDATED RESULTS")
print("="*55)
for sys, s in summary.items():
    print(f"\n{sys}")
    print(f"  Faithfulness:     {s['faithfulness']:.3f}")
    print(f"  Answer relevancy: {s['answer_relevancy']:.3f}")
    print(f"  Context recall:   {s['context_recall']:.3f}")

print("\nSaved: benchmark_scores_detail.csv, benchmark_summary.json")
