# SciRet v2 Code Documentation — Part 3 (Runbook: Runtime, Memory, Kaggle)

This document is the operational runbook for executing SciRet v2 reliably.

It focuses on:
- expected runtime by stage,
- memory/disk planning,
- Tier 1 vs Tier 2 execution strategy,
- Kaggle notebook workflow order,
- practical recovery steps when a run fails.

---

## 1) Execution Philosophy

Use this rule at all times:

1. Build and debug on **Tier 1** first.
2. Freeze config.
3. Run the same logic on **Tier 2**.
4. Report paper numbers from Tier 2.

Only scale changes; code path should remain constant.

---

## 2) Recommended Runtime Expectations (Baseline Planning)

Times vary by machine and model choice. Use this as planning guidance.

## Tier 1 (1,000 papers)

- `01_data_exploration`: ~1-5 min
- `02_text_chunking`: ~1-10 min
- `03_embedding_baseline`:
  - current stub: very fast
  - real BGE-M3: ~20 min to 2+ hours (hardware-dependent)
- `04_hybrid_retrieval`: ~1-15 min
- `05_reranking`: ~5-40 min (depends on candidate size/model)
- `06_figure_extraction`: ~10-60 min (PDF parsing overhead)
- `07_clip_embeddings`: ~10-60 min
- `08_multimodal_pipeline`: ~5-20 min
- `09_evaluation`: ~5-30 min

## Tier 2 (50,000 papers)

- `01_data_exploration`: ~10-60 min
- `02_text_chunking`: ~30 min to few hours
- `03_embedding_baseline` (real model): several hours to multi-day depending batch/device
- `04`/`05`: few hours depending retrieval candidate depth and reranker usage
- `06`/`07`: can be long if many PDFs/figures are processed
- `08`/`09`: depends mostly on evaluation set size and generation cost

---

## 3) Memory and Disk Planning

## Local (Tier 1)

- Keep only required artifacts:
  - cleaned papers,
  - chunks,
  - embeddings/index,
  - result tables.
- Delete temporary intermediates aggressively.
- Prefer parquet over CSV for large intermediate tables.

## Kaggle (Tier 2)

- Respect disk limit (~30GB free tier practical constraint).
- Save only essential outputs:
  - index shards,
  - retrieval runs,
  - metric tables/plots,
  - manifests/config snapshots.
- Use chunked processing and periodic checkpoint writes.

---

## 4) Cache Strategy (Must Follow)

For expensive steps (`03`, `07`, reranker batches):

1. Check cache existence first.
2. Validate cache compatibility (model/config/version).
3. Reuse cache if valid.
4. Recompute only if config changed.

Recommended manifest fields:

- `model_name`
- `model_version` (if known)
- `chunk_size`
- `overlap`
- `tier_name`
- `created_at`
- `row_count`

---

## 5) Tier Configuration Template

Maintain one config object per run:

```text
tier_name: tier1 | tier2
tier_size: 1000 | 50000
seed: 42
chunk_size: 400
overlap: 50
embed_model: BAAI/bge-m3
reranker_model: cross-encoder/ms-marco-MiniLM-L-6-v2
fusion_method: rrf
top_k_dense: 100
top_k_sparse: 100
top_k_final: 5
```

Do not silently change these between experiments.

---

## 6) Exact Stage Order for Local (Tier 1)

Run in this order:

1. `01_data_exploration.ipynb`
2. `02_text_chunking.ipynb`
3. `03_embedding_baseline.ipynb`
4. `04_hybrid_retrieval.ipynb`
5. `05_reranking.ipynb`
6. `09_evaluation.ipynb`
7. (optional multimodal) `06` -> `07` -> `08` -> `09`

After each notebook:
- verify output file exists,
- record run note (time, success/failure, config),
- stop and fix if outputs are inconsistent.

---

## 7) Kaggle Runbook (Tier 2)

Kaggle often works best as one orchestrated notebook, but keep logical sections matching `01` to `09`.

## Section structure inside Kaggle notebook

1. **Setup**
   - install/import dependencies
   - define paths
   - load config

2. **Data prep (01)**
   - load `metadata.csv`
   - apply same filters
   - save cleaned subset

3. **Chunking (02)**
   - run same chunk config as Tier 1
   - save chunks parquet

4. **Embeddings (03)**
   - cache-or-build
   - periodically checkpoint

5. **Retrieval + rerank (04/05)**
   - run on evaluation queries
   - save ranked outputs

6. **Multimodal path (06/07/08)**
   - only if in current experiment scope

7. **Evaluation (09)**
   - compute metrics
   - export tables/plots

8. **Export artifacts**
   - zip essential outputs
   - attach/download from Kaggle output

---

## 8) Failure Recovery Playbook

## If kernel restarts mid-run

- Resume from last completed artifact.
- Do not rerun full pipeline unless cache invalid.
- Re-open manifest and confirm config consistency.

## If embeddings fail late in long run

- Reduce batch size.
- Write partial shard outputs every N batches.
- Merge shards at end.

## If retrieval outputs look wrong

- confirm chunk IDs align between chunk table and embedding table,
- confirm no stale mixed-tier index is being used,
- rerun top-5 debug query and inspect returned text chunks manually.

## If metrics are unexpectedly poor

- verify evaluation labels,
- verify query set not leaking into tuning,
- compare text-only vs multimodal under same candidate budget.

---

## 9) Paper-Facing Artifact Checklist

Before writing final results section, ensure you have:

- frozen run config files,
- run manifests per experiment,
- retrieval ranking outputs,
- metric tables (raw + aggregated),
- variance/bootstrapping notes if applicable,
- error analysis examples with citations.

This prevents last-minute “where did this number come from?” issues.

---

## 10) Practical Weekly Routine

Recommended weekly cycle:

1. Monday-Tuesday: implement or refactor one stage.
2. Wednesday: Tier 1 validation and bug fixes.
3. Thursday-Friday: Tier 2 execution on Kaggle.
4. Weekend: analyze outputs + update paper notes.

Keep a single experiment log:
- date,
- git commit,
- config hash,
- key results,
- issues encountered,
- next action.

---

## 11) What to Do Next (Immediate)

1. Run Tier 1 full text-only chain (`01`->`05`->`09`).
2. Save first reproducible comparison table.
3. Replace placeholder embedder/reranker with real models.
4. Re-run Tier 1 and confirm metrics pipeline is stable.
5. Scale exactly same config to Tier 2 on Kaggle.

This gives you a publishable execution path with minimal chaos.
