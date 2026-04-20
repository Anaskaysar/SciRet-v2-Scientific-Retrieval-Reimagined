"""
SciRet — Flask Web Application
Run: python app.py
"""

import os, sys, pickle, warnings, json
from pathlib import Path

APP_DIR      = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "2_src"))

os.environ.setdefault("SCIRET_TIER", "tier1")
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from flask import Flask, render_template, request, jsonify
import logging

# Suppress cross-encoder/transformers loading warnings
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

# ── load config ────────────────────────────────────────────────────────────
from config import get_config
CFG = get_config()
print(f"[SciRet Flask] {CFG.summary()}")

DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── load models and indexes ────────────────────────────────────────────────
print("Loading models and indexes...")

chunks_df    = pd.read_parquet(CFG.chunks_path)
chunk_lookup = chunks_df.set_index("chunk_id").to_dict("index")

# ensure journal column exists even if not in parquet
if "journal" not in chunks_df.columns:
    chunks_df["journal"] = ""
if "publish_time" not in chunks_df.columns:
    chunks_df["publish_time"] = ""

embedder = SentenceTransformer("BAAI/bge-m3", device=DEVICE)
embedder.max_seq_length = 512

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)

chroma_client = chromadb.PersistentClient(path=str(CFG.chroma_dir))
text_col      = chroma_client.get_collection(CFG.text_collection)

bm25_path = CFG.embeddings_dir / "bm25_index.pkl"
with open(bm25_path, "rb") as f:
    bm25, bm25_ids = pickle.load(f)

CHUNK_COUNT = text_col.count()
print(f"Ready — {CHUNK_COUNT:,} chunks indexed on {DEVICE.upper()}")

# ── retrieval ──────────────────────────────────────────────────────────────
STAGE1_K = 50
TOP_K    = 5
RRF_K    = 60

def rrf(ranked_lists, k=RRF_K):
    scores = {}
    for rl in ranked_lists:
        for rank, doc_id in enumerate(rl, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def retrieve(query: str, use_reranker: bool = False):
    q_emb = embedder.encode([query], normalize_embeddings=True)
    dense = text_col.query(
        query_embeddings=q_emb.tolist(),
        n_results=STAGE1_K,
        include=["metadatas", "distances"],
    )
    d_ids = dense["ids"][0]

    toks  = query.lower().split()
    b_scr = bm25.get_scores(toks)
    b_ids = [bm25_ids[i] for i in np.argsort(b_scr)[::-1][:STAGE1_K]]

    fused = rrf([d_ids, b_ids])
    candidates = []
    for cid, rrf_score in fused[:STAGE1_K]:
        if cid in chunk_lookup:
            row = chunk_lookup[cid]
            candidates.append({
                "chunk_id"  : cid,
                "title"     : row.get("title", "Unknown"),
                "chunk_text": row.get("chunk_text", ""),
                "journal"   : row.get("journal", ""),
                "rrf_score" : round(rrf_score, 4),
                "rerank_score": None,
            })

    if use_reranker and candidates:
        pairs  = [(query, c["chunk_text"]) for c in candidates]
        scores = reranker.predict(pairs, show_progress_bar=False)
        for c, s in zip(candidates, scores):
            c["rerank_score"] = round(float(s), 3)
        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    return candidates[:TOP_K]


# ── generation ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are SciRet, a scientific research assistant helping the general public "
    "understand COVID-19 research. Answer ONLY using the provided passages. "
    "Do not use outside knowledge. Cite passages as [1], [2], etc. "
    "Write clearly for a general audience — avoid unnecessary jargon. "
    "If the context is insufficient, say so honestly. Answer in 4-6 sentences."
)

def generate_answer(query: str, passages: list) -> dict:
    if not GEMINI_KEY:
        return {
            "answer": None,
            "error": "GEMINI_API_KEY not set. Showing retrieved passages only.",
        }
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        llm = genai.GenerativeModel("gemini-1.5-flash")
        ctx = "\n\n".join(
            f"[{i}] From: \"{p['title']}\"\n{p['chunk_text'][:500]}"
            for i, p in enumerate(passages, 1)
        )
        prompt = f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{ctx}\n\nQUESTION: {query}\n\nANSWER:"
        resp = llm.generate_content(prompt)
        return {"answer": resp.text.strip(), "error": None}
    except Exception as e:
        return {"answer": None, "error": str(e)}


# ── Flask app ──────────────────────────────────────────────────────────────
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html", chunk_count=CHUNK_COUNT)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api/query", methods=["POST"])
def api_query():
    data         = request.get_json()
    query        = (data.get("query") or "").strip()
    use_reranker = bool(data.get("use_reranker", False))

    if not query:
        return jsonify({"error": "Empty query"}), 400

    passages  = retrieve(query, use_reranker)
    gen_result = generate_answer(query, passages)

    return jsonify({
        "query"    : query,
        "answer"   : gen_result["answer"],
        "gen_error": gen_result["error"],
        "passages" : passages,
        "reranker" : use_reranker,
    })

@app.route("/api/status")
def api_status():
    return jsonify({
        "chunks"  : CHUNK_COUNT,
        "device"  : DEVICE,
        "gemini"  : bool(GEMINI_KEY),
        "tier"    : "tier1",
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
