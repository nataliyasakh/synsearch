"""
score_benchmark.py — Custom LLM-as-judge scorer.

Reads benchmark_results.csv (already saved) and scores each answer on:
  - Faithfulness: does the answer stick to the retrieved context?
  - Answer Relevancy: does the answer address the question?
  - Context Recall: does the context contain what's needed to answer?

Uses Groq directly — no RAGAS, no async, no hanging.
Methodology is identical to RAGAS; we just call the judge ourselves.

Run:  python score_benchmark.py
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

# ── Judge calls ───────────────────────────────────────────────────────────────

def judge(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            r = groq_client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(15 * (attempt + 1))
            else:
                return "0.5"   # neutral fallback

def extract_score(text: str) -> float:
    """Pull the first number 0-1 out of a judge response."""
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

def score_faithfulness(question, answer, contexts) -> float:
    """Does the answer only use information present in the contexts?"""
    ctx_str = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
    prompt = f"""You are an impartial judge evaluating whether an AI answer is faithful to its source documents.

Question: {question}
Answer: {answer}
Source contexts:
{ctx_str}

Score the faithfulness of the answer on a scale from 0.0 to 1.0.
- 1.0 = every claim in the answer is directly supported by the contexts
- 0.5 = some claims are supported, some are not
- 0.0 = the answer contains information not present in the contexts

Reply with ONLY a number between 0.0 and 1.0."""
    return extract_score(judge(prompt))

def score_relevancy(question, answer) -> float:
    """Does the answer actually address the question asked?"""
    prompt = f"""You are an impartial judge evaluating whether an AI answer is relevant to the question.

Question: {question}
Answer: {answer}

Score the relevancy on a scale from 0.0 to 1.0.
- 1.0 = the answer directly and completely addresses the question
- 0.5 = the answer partially addresses the question
- 0.0 = the answer is off-topic or does not address the question

Reply with ONLY a number between 0.0 and 1.0."""
    return extract_score(judge(prompt))

def score_context_recall(question, answer, ground_truth, contexts) -> float:
    """Does the retrieved context contain enough to answer correctly?"""
    ctx_str = "\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))
    prompt = f"""You are an impartial judge evaluating whether retrieved context contains the information needed to answer a question correctly.

Question: {question}
Correct answer: {ground_truth}
Retrieved contexts:
{ctx_str}

Score the context recall on a scale from 0.0 to 1.0.
- 1.0 = the contexts contain all the information needed to produce the correct answer
- 0.5 = the contexts contain some relevant information
- 0.0 = the contexts contain no useful information for answering this question

Reply with ONLY a number between 0.0 and 1.0."""
    return extract_score(judge(prompt))

# ── Load saved answers ────────────────────────────────────────────────────────
df = pd.read_csv("benchmark_results.csv")
print(f"Loaded {len(df)} rows\n")

# Re-retrieve contexts
def retrieve(query):
    q_vec = embedder.encode([query], normalize_embeddings=True)[0].tolist()
    res = index.query(vector=q_vec, top_k=5, include_metadata=True)
    return [m.metadata.get("text", m.metadata.get("title",""))[:500]
            for m in res.matches]

# ── Score all three systems ───────────────────────────────────────────────────
results = {"a": [], "b": [], "c": []}

print("Scoring (3 metrics × 3 systems × 50 questions = 450 judge calls)")
print("~20 min with rate limit pauses. Progress shown per question.\n")

for i, row in df.iterrows():
    q  = row["question"]
    gt = row["ground_truth"]
    ctx = retrieve(q)
    n = i + 1

    print(f"[{n:02d}/50] scoring...", end=" ", flush=True)

    # System A — bare (no retrieval, use empty context)
    fa = score_faithfulness(q, str(row["answer_a"]), ["no retrieval context"])
    ra = score_relevancy(q, str(row["answer_a"]))
    ca = score_context_recall(q, str(row["answer_a"]), gt, ["no retrieval context"])
    results["a"].append({"faithfulness": fa, "relevancy": ra, "recall": ca})
    time.sleep(2)

    # System B — fast model + RAG
    fb = score_faithfulness(q, str(row["answer_b"]), ctx)
    rb = score_relevancy(q, str(row["answer_b"]))
    cb = score_context_recall(q, str(row["answer_b"]), gt, ctx)
    results["b"].append({"faithfulness": fb, "relevancy": rb, "recall": cb})
    time.sleep(2)

    # System C — large model + RAG
    fc = score_faithfulness(q, str(row["answer_c"]), ctx)
    rc = score_relevancy(q, str(row["answer_c"]))
    cc = score_context_recall(q, str(row["answer_c"]), gt, ctx)
    results["c"].append({"faithfulness": fc, "relevancy": rc, "recall": cc})
    time.sleep(3)

    print(f"A({fa:.2f}/{ra:.2f}/{ca:.2f}) "
          f"B({fb:.2f}/{rb:.2f}/{cb:.2f}) "
          f"C({fc:.2f}/{rc:.2f}/{cc:.2f})")

# ── Aggregate ─────────────────────────────────────────────────────────────────
def avg(lst, key):
    return round(sum(x[key] for x in lst) / len(lst), 3)

summary = {
    "Bare Groq (no retrieval)": {
        "faithfulness":     avg(results["a"], "faithfulness"),
        "answer_relevancy": avg(results["a"], "relevancy"),
        "context_recall":   avg(results["a"], "recall"),
    },
    "Groq fast + SynSearch RAG": {
        "faithfulness":     avg(results["b"], "faithfulness"),
        "answer_relevancy": avg(results["b"], "relevancy"),
        "context_recall":   avg(results["b"], "recall"),
    },
    "Groq large + SynSearch RAG": {
        "faithfulness":     avg(results["c"], "faithfulness"),
        "answer_relevancy": avg(results["c"], "relevancy"),
        "context_recall":   avg(results["c"], "recall"),
    },
}

with open("benchmark_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# Per-question detail
with open("benchmark_scores_detail.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["question",
                "a_faith","a_rel","a_recall",
                "b_faith","b_rel","b_recall",
                "c_faith","c_rel","c_recall"])
    for i, row in df.iterrows():
        a, b, c = results["a"][i], results["b"][i], results["c"][i]
        w.writerow([row["question"],
                    a["faithfulness"],a["relevancy"],a["recall"],
                    b["faithfulness"],b["relevancy"],b["recall"],
                    c["faithfulness"],c["relevancy"],c["recall"]])

print("\n" + "="*55)
print("RESULTS")
print("="*55)
for sys, s in summary.items():
    print(f"\n{sys}")
    print(f"  Faithfulness:     {s['faithfulness']:.3f}")
    print(f"  Answer relevancy: {s['answer_relevancy']:.3f}")
    print(f"  Context recall:   {s['context_recall']:.3f}")

print("\nSaved: benchmark_summary.json, benchmark_scores_detail.csv")
