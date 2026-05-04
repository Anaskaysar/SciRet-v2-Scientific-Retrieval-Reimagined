# SciRet Notebooks — Restructured May 2026

## How This Works

This folder supports the **scale law study** for the EMNLP 2026 paper.
The design runs an identical pipeline at 6 corpus sizes to empirically
characterize how BM25 vs dense retrieval performance changes with scale.

## Folder Map

```
General/              ← Run ONCE. Shared across all scale experiments.
  00_environment.ipynb      Environment check, package versions
  01_dataset_stats.ipynb    Full CORD-19 corpus statistics
  02_chunking_strategy.ipynb  4-strategy chunking comparison (done once)
  03_query_set.ipynb        Define + save the 50 evaluation queries (FIXED ground truth)
  04_cross_tier_analysis.ipynb  Fit scale curves after all tiers complete

scale_1K/             ← 1,000 papers  (local CPU, ~5 min)
scale_5K/             ← 5,000 papers  (local GPU, ~20 min)
scale_15K/            ← 15,000 papers (Kaggle T4, ~45 min)
scale_30K/            ← 30,000 papers (Kaggle T4, ~90 min)
scale_50K/            ← 50,000 papers (Kaggle T4, ~75 min) ← PRIMARY REPORTING TIER
scale_75K/            ← 75,000 papers  [only if professor provides compute]
scale_100K/           ← 100,000 papers [only if professor provides compute]
```

## Each Scale Folder Contains

```
01_sample_chunk.ipynb     Sample N papers (stratified by year), build chunks
02_embed.ipynb            BGE-M3 dense embeddings + BM25 index
03_retrieval_ablation.ipynb  Recall@K for dense / BM25 / hybrid
04_reranking.ipynb        Precision@K with vs without cross-encoder
05_generation_ragas.ipynb RAGAS with Gemini 1.5 Flash  [Kaggle/GPU tiers only]
```

## Stopping Criterion

After running scale_1K → scale_30K, check the delta table in
`General/04_cross_tier_analysis.ipynb`. If the BM25/dense R@1 gap
is no longer changing meaningfully between consecutive tiers,
the curve has saturated and you do not need 75K/100K.

## Key Code Fixes vs Previous Notebooks

See `General/FIXES.md` for the full list. Critical ones:
1. DEVICE variable defined in every config cell
2. RAGAS uses Gemini wrapper (not OpenAI)
3. Ground truth loaded from fixed file, NOT derived from the retrieval system being tested
4. DPR comparison cell has DEVICE fix applied
5. RRF k=60 is explicit and noted in output

## Legacy

Old notebooks (tier_1, tier_2, Alamin) are archived at:
`6_legacy/notebooks_archived_2026-05-04/`
