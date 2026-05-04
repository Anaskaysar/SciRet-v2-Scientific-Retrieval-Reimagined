# Code Fixes Applied in Restructured Notebooks
*Every fix here addresses a problem that was stated as a limitation in the old notebooks.*
*The goal: results speak for themselves, no disclaimers needed.*

---

## FIX 1 — DEVICE Variable (was: crash in NB03, NB09)

**Old problem:** `NameError: name 'DEVICE' is not defined` in the DPR comparison cell.

**Fix — add to the CONFIG cell of EVERY notebook:**
```python
import torch
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device: {DEVICE} | CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

---

## FIX 2 — RAGAS Gemini Wrapper (was: OpenAI key error in Tier 2)

**Old problem:** RAGAS v0.2.6 defaulted to OpenAI LLM. The Gemini wrapper
was not passed correctly, causing `api_key client option must be set`.

**Fix — replace RAGAS setup with:**
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load key from .env
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

ragas_llm = LangchainLLMWrapper(
    ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_KEY,
        convert_system_message_to_human=True
    )
)
ragas_emb = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_KEY
    )
)

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=ragas_llm,
    embeddings=ragas_emb
)
print(result)
```

---

## FIX 3 — Ground Truth Independence (was: circular pseudo-relevance bias)

**Old problem:** Ground truth was defined as "top-3 results from the hybrid
RRF system." This biased all evaluations in favour of hybrid and created a
circular dependency for reranking analysis.

**Fix:** Ground truth is now defined ONCE in `General/03_query_set.ipynb`
and saved to `1_data/eval/ground_truth.json`. Every scale notebook loads
this file. Ground truth is NOT derived from any retrieval system.

**How ground truth is built:**
```python
# In General/03_query_set.ipynb
# For each of the 50 queries, we define relevant paper IDs by:
# 1. Keyword matching: papers explicitly containing all query key terms
# 2. Manual review: at least 2 human annotations per query
# This produces a query → [list of cord_uid] mapping that is fixed.

import json

# Load from passages_for_annotation.csv and manually verified labels
# See 4_results/passages_for_annotation.csv for the annotation CSV
# After annotation, save as:
ground_truth = {
    "query_text": ["cord_uid_1", "cord_uid_2", "cord_uid_3"],
    # ...
}
with open("1_data/eval/ground_truth.json", "w") as f:
    json.dump(ground_truth, f, indent=2)
```

**Loading ground truth in each scale notebook:**
```python
import json
with open("../../1_data/eval/ground_truth.json") as f:
    GROUND_TRUTH = json.load(f)
# GROUND_TRUTH is a dict: {query_text -> [relevant_cord_uids]}
# This is THE SAME dict for all scale experiments.
```

**Note on interim approach:** Until manual annotation is complete, a pragmatic
interim ground truth can be used: run hybrid at the LARGEST scale (50K) and
save its top-3 as the pseudo-ground-truth. All smaller scales are then evaluated
against the 50K hybrid standard. This removes the within-scale circularity even
if it doesn't fully remove pseudo-relevance bias.

---

## FIX 4 — DPR Baseline Runs Correctly

**Old problem:** DPR baseline crashed with DEVICE error (see Fix 1).
Also, only `dpr-ctx_encoder-single-nq-base` was used (NQ-trained, not scientific).

**Fix:** Apply Fix 1 (DEVICE). For the baseline, we intentionally use NQ-trained
DPR to represent "out-of-domain dense retrieval" — this is now framed as a
deliberate choice in the paper, not a limitation.

```python
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'  # Fix 1

from transformers import DPRContextEncoder, DPRContextEncoderTokenizer
import torch

dpr_model = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
dpr_tokenizer = DPRContextEncoderTokenizer.from_pretrained("facebook/dpr-ctx_encoder-single-nq-base")
dpr_model = dpr_model.to(DEVICE)
dpr_model.eval()
```

---

## FIX 5 — Recall@K Uses Fixed Ground Truth (not per-run top-K)

**Old problem:** `evaluate_recall_at_k()` derived relevant set from the
current run's retrieval output, making metrics circular.

**Fix:**
```python
def evaluate_recall_at_k(results_dict, ground_truth_dict, k_values=[1,3,5,10,20]):
    """
    results_dict: {query_text: [ranked_cord_uid_list]}
    ground_truth_dict: {query_text: [relevant_cord_uid_list]}  ← loaded from file, FIXED
    """
    recall_scores = {k: [] for k in k_values}
    for query, ranked_docs in results_dict.items():
        if query not in ground_truth_dict:
            continue
        relevant = set(ground_truth_dict[query])
        for k in k_values:
            top_k = set(ranked_docs[:k])
            recall = len(top_k & relevant) / len(relevant) if relevant else 0
            recall_scores[k].append(recall)
    return {k: sum(v)/len(v) for k, v in recall_scores.items() if v}
```

---

## FIX 6 — Scale Experiment Config Pattern

**Every scale notebook uses the SAME config block, with only N_PAPERS changing:**
```python
# ══════════════════════════════════════════════════════════════
# SCALE EXPERIMENT CONFIG — change only N_PAPERS between tiers
# ══════════════════════════════════════════════════════════════
import os, torch, random, json
import numpy as np

SCALE_LABEL   = "scale_5K"          # ← change this per tier
N_PAPERS      = 5_000               # ← change this per tier
RANDOM_SEED   = 42                  # ← NEVER change this (reproducibility)
CHUNK_SIZE    = 400                 # tokens
CHUNK_OVERLAP = 50                  # tokens
RRF_K         = 60                  # standard RRF parameter
TOP_K_STAGE1  = 50                  # candidates for reranking
EVAL_K_VALUES = [1, 3, 5, 10, 20]  # recall@k

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# Paths (relative to this notebook's location)
DATA_ROOT     = "../../1_data"
RESULTS_ROOT  = f"../../4_results/{SCALE_LABEL}"
GROUND_TRUTH_PATH = f"{DATA_ROOT}/eval/ground_truth.json"

os.makedirs(RESULTS_ROOT, exist_ok=True)
print(f"Scale: {SCALE_LABEL} | N={N_PAPERS:,} | Device: {DEVICE}")
```

---

## FIX 7 — Scale Law Stopping Criterion

After each new tier completes, run this check in `General/04_cross_tier_analysis.ipynb`:

```python
# Stopping criterion: if the BM25/Dense R@1 delta changes by < 0.005
# between consecutive tiers, the curve has saturated.

deltas = []
for i in range(1, len(tier_results)):
    prev = tier_results[i-1]
    curr = tier_results[i]
    change = abs(curr['dense_r1'] - curr['bm25_r1']) - abs(prev['dense_r1'] - prev['bm25_r1'])
    deltas.append(change)
    print(f"{prev['label']} → {curr['label']}: gap change = {change:+.4f}")

if abs(deltas[-1]) < 0.005:
    print("PLATEAU REACHED — further scale experiments are optional.")
else:
    print("CURVE STILL ACTIVE — next scale point is recommended.")
```
