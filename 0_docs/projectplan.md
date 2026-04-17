# SciRet v2 — Project completion plan and instructions

**Source of truth for research scope:** `0_docs/SciRet_v2_Research_Proposal.docx`  
**Technical overview / public spec:** `README.md`  
**Operational constraints (dataset scale, platforms):** `truth.md` (if present locally)

Whenever the proposal and README disagree, follow the **proposal**.

---

## 1. Goals (what “done” means)

1. **System:** Multimodal RAG over a CORD-19 subset — text chunks, figures, tables — with hybrid retrieval (BM25 + dense), reranking, and grounded answer generation (+ optional visual QA path).
2. **Research:** Answer RQs in the README/proposal (multimodal vs text-only, comparison to SciRet v1, fusion strategies, hallucination mitigation).
3. **Artifacts:** Reproducible code (`2_src`), notebooks for exploration, evaluation outputs (`4_results`), Gradio demo (`5_app`), and a paper / preprint path (ECIR / ACL workshop / arXiv as targeted in README).
4. **Demo:** Replace dummy retrieval in `gradio_app.py` with the real pipeline; optional Hugging Face Space.

---

## 2. Dataset strategy (instructions)

- Use a **tiered subset** (see `truth.md`):
  - **Tier 1 (~1k papers):** Local development — fast iteration, all pipeline debugging.
  - **Tier 2 (~50k papers):** Kaggle (attach CORD-19 dataset) — main reported retrieval metrics.
  - **Tier 3 (full CORD-19):** Optional; not required for a credible publication if Tier 2 is well-defined.
- Fix **inclusion rules** once: metadata vs full text, PDF availability, language, deduplication, path mapping from `metadata.csv` to JSON/PDFs.
- Persist **stable IDs** for papers, chunks, figures, and tables; log them in retrieval and evaluation.

---

## 3. Phase plan (execution order)

### Phase A — Scope and evaluation protocol (1–2 weeks)

**Deliverable:** Written experiment protocol (corpus, splits, systems, metrics, seeds, hardware).

**Tasks:**

1. Define **query set** and task types (open QA, evidence finding, figure/table-centric). Reserve held-out queries for final numbers.
2. Define **systems to compare:**
   - S0: SciRet v1 (legacy) on same subset where feasible.
   - S1: SciRet v2 text-only (modern stack).
   - S2: SciRet v2 multimodal.
   - S3+: At least two **fusion** variants if RQ3 is in scope (e.g. late fusion vs caption-augmented text).
3. Fix **metrics:** retrieval (Recall@K, MRR, NDCG); generation (RAGAS-style faithfulness, relevance, groundedness); **citation** rules; optional small human audit for RQ4.

### Phase B — Data pipeline (2–4 weeks)

**Deliverable:** Tier 1 fully processed; reproducible loaders and exports.

**Tasks:**

1. Ingest CORD-19 (`metadata.csv` + body text / PDFs per your rules).
2. Text: clean, chunk (pick one strategy and document parameters), export chunk table + metadata.
3. PDFs: figures (e.g. PyMuPDF) → images + bbox/page metadata; tables (e.g. pdfplumber) → serialised text; track failures.
4. Output layout: processed manifest (CSV/Parquet) + chunk store + asset paths; align with intended `2_src/data/` modules (`loader.py`, `chunker.py`, `pdf_parser.py`) by refactoring from notebooks when stable.

### Phase C — Text-only RAG baseline (3–5 weeks)

**Deliverable:** S1 end-to-end on Tier 1; ablations documented.

**Tasks:**

1. Dense embeddings (e.g. BGE-M3) + ChromaDB (or chosen store).
2. BM25 on same chunks; **hybrid** search with RRF (or equivalent).
3. Cross-encoder **rerank** (top-100 → top-k).
4. Generator (Mistral 7B or API) with **citations** and fixed decoding settings.
5. Single pipeline API (e.g. load index → `query()` → answer + sources + debug).

### Phase D — Multimodal extension (4–8 weeks)

**Deliverable:** S2 on Tier 1, then Tier 2 for paper numbers.

**Tasks:**

1. Figure embeddings (e.g. CLIP); optional captions (e.g. BLIP-2) as text for retrieval.
2. **Query routing** (text vs figure-heavy queries).
3. **Fusion experiments** for RQ3 with fair budgets (same k, same reranker where applicable).
4. Visual QA (e.g. LLaVA) only when figures are in context; define limits.

### Phase E — Hallucination mitigation (RQ4) (2–4 weeks; can overlap D)

**Deliverable:** “+ verification” variant vs baseline metrics.

**Tasks:**

1. Claim-level grounding / NLI-style check against retrieved passages.
2. Citation integrity checks (cited IDs must be in retrieved set).
3. Error analysis sample for the paper discussion.

### Phase F — Full evaluation (2–3 weeks)

**Deliverable:** `4_results/` tables + plots; README comparison table filled.

**Tasks:**

1. Freeze configs; run on Tier 2 for all systems in scope.
2. Report compute cost and environment.
3. Bootstrap or variance on query set where possible.

### Phase G — Demo and dissemination (2–4 weeks)

**Deliverable:** Working Gradio app on real backend; paper draft; optional HF Space.

**Tasks:**

1. Wire `5_app/gradio_app.py` to pipeline (text-only first, then multimodal).
2. Package small index or retrieval strategy suitable for hosting limits.
3. Write paper; submit to target venue + arXiv per proposal timeline.

---

## 4. Repository hygiene (instructions)

- Large data and generated indices stay **out of git** (see `.gitignore`).
- Ensure **proposal path** is ignored if you do not want it public: e.g. `0_docs/SciRet_v2_Research_Proposal.docx` (root-only ignore may miss `0_docs/` copies).
- Migrate proven notebook code into **`2_src/`** for reproducibility; keep notebooks for exploration and figures.

---

## 5. Weekly operating instructions

1. **Always** validate on Tier 1 before scaling to Kaggle / Tier 2.
2. After each phase, write a **short changelog** (what works, what failed, next command).
3. **Pin** dependency versions for any run that produces paper numbers (`requirements.txt` or export).
4. Keep **one** canonical chunking and indexing config; branch configs only for ablations, with clear names.

---

## 6. Immediate next actions (checklist)

- [ ] Read `0_docs/SciRet_v2_Research_Proposal.docx` and list any milestones not covered above; merge into Phase A.
- [ ] Fix Tier 1 subset and document selection query.
- [ ] Finish EDA + chunking notebook outputs → stable processed files.
- [ ] Implement or stub `2_src` layout to match README; connect Gradio to stub then real retriever.
- [ ] Draft 20–50 seed queries with rough relevance labels for early retrieval tuning.

---

*End of plan document.*