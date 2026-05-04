"""
SciRet — central tier/path/model config.

Single source of truth for notebooks AND source modules so the exact same
codebase runs on:
  * Tier 1  — local laptop, 1k CORD-19 papers, CPU, debugging
  * Tier 2  — Kaggle, 50k papers, GPU, paper experiments
  * Tier 3  — optional full CORD-19 if compute becomes available

Switching tiers is a one-line change:
    export SCIRET_TIER=tier2            # shell
    os.environ["SCIRET_TIER"] = "tier2"  # notebook
or pass tier="tier2" to get_config().

Every artifact (chunks, embeddings, Chroma collections, results) is namespaced
by tier so tiers can coexist on the same machine without cross-contamination.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

TIER_SIZES: Dict[str, int] = {
    "tier1": 1_000,    # local dev
    "tier2": 50_000,   # Kaggle main experiments
    "tier3": -1,       # full CORD-19 (no cap)
}

# Chunking parameters — FROZEN across tiers for paper reproducibility.
CHUNK_SIZE_TOKENS: int = 400
CHUNK_OVERLAP_TOKENS: int = 50
MIN_TOKENS_PER_CHUNK: int = 20

# Model identifiers — FROZEN.
BGE_M3_MODEL: str = "BAAI/bge-m3"
BGE_M3_DIM: int = 1024
DPR_QUESTION_MODEL: str = "facebook/dpr-question_encoder-single-nq-base"
DPR_CONTEXT_MODEL: str = "facebook/dpr-ctx_encoder-single-nq-base"
DPR_DIM: int = 768
CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CLIP_MODEL: str = "openai/clip-vit-base-patch32"
CLIP_DIM: int = 512
BLIP2_MODEL: str = "Salesforce/blip2-opt-2.7b"
LLAVA_MODEL: str = "llava-hf/llava-1.5-7b-hf"
GEMINI_MODEL: str = "gemini-2.0-flash"
MISTRAL_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"

# Retrieval hyperparameters — FROZEN.
DENSE_TOP_K: int = 100
SPARSE_TOP_K: int = 100
RRF_K: int = 60
RERANK_TOP_K: int = 5
SEED: int = 42


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _find_project_root(start: Path | None = None) -> Path:
    """Walk upward looking for the SciRet root (has `2_src/` and `readme.md`)."""
    p = (start or Path(__file__)).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "2_src").is_dir() and (candidate / "readme.md").is_file():
            return candidate
    # fallback: two levels up from this file (2_src/config.py -> project root)
    return Path(__file__).resolve().parents[1]


@dataclass
class SciRetConfig:
    tier: str = "tier1"
    project_root: Path = field(default_factory=_find_project_root)

    # --- paths (derived) ---
    @property
    def tier_size(self) -> int:
        return TIER_SIZES[self.tier]

    @property
    def data_dir(self) -> Path:
        return self.project_root / "1_data"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed" / self.tier

    @property
    def embeddings_dir(self) -> Path:
        return self.data_dir / "embeddings" / self.tier

    @property
    def figures_dir(self) -> Path:
        return self.data_dir / "figures" / self.tier

    @property
    def pdf_dir(self) -> Path:
        return self.raw_dir / "pdfs"

    @property
    def chroma_dir(self) -> Path:
        return self.embeddings_dir / "chroma_db"

    @property
    def results_dir(self) -> Path:
        return self.project_root / "4_results" / self.tier

    @property
    def src_dir(self) -> Path:
        return self.project_root / "2_src"

    # --- file paths ---
    @property
    def papers_clean_path(self) -> Path:
        if self.tier == "tier2":
            return self.processed_dir / "papers_tier2.parquet"
        return self.processed_dir / "papers_clean.parquet"

    @property
    def chunks_path(self) -> Path:
        if self.tier == "tier2":
            return self.processed_dir / "chunks_tier2.parquet"
        return self.processed_dir / "chunks.parquet"

    @property
    def figures_metadata_path(self) -> Path:
        if self.tier == "tier2":
            return self.processed_dir / "figures_metadata_tier2.parquet"
        return self.processed_dir / "figures_metadata.parquet"

    @property
    def bm25_path(self) -> Path:
        if self.tier == "tier2":
            # For tier2, files are in an extra 'embeddings' subfolder
            return self.embeddings_dir / "embeddings" / "bm25_tier2.pkl"
        return self.embeddings_dir / "bm25_index.pkl"

    @property
    def tier_manifest_path(self) -> Path:
        return self.processed_dir / "tier_manifest.json"

    @property
    def multimodal_config_path(self) -> Path:
        return self.src_dir / f"multimodal_config_{self.tier}.json"

    # --- Chroma collection names ---
    @property
    def text_collection(self) -> str:
        return f"sciret_{self.tier}_bge_m3_cs{CHUNK_SIZE_TOKENS}_o{CHUNK_OVERLAP_TOKENS}"

    @property
    def figure_collection(self) -> str:
        return f"sciret_{self.tier}_clip_vitb32"

    # --- runtime helpers ---
    def ensure_dirs(self) -> None:
        for d in [
            self.raw_dir,
            self.processed_dir,
            self.embeddings_dir,
            self.figures_dir,
            self.chroma_dir,
            self.results_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def summary(self) -> str:
        return (
            f"[SciRet:{self.tier}] size={self.tier_size} "
            f"root={self.project_root} chunks={self.chunks_path.name} "
            f"chroma={self.chroma_dir.name}/{self.text_collection}"
        )


def get_config(tier: str | None = None) -> SciRetConfig:
    """
    Resolve tier from (in order):
        1) explicit argument
        2) SCIRET_TIER env var
        3) default "tier1"
    """
    t = tier or os.environ.get("SCIRET_TIER", "tier1")
    if t not in TIER_SIZES:
        raise ValueError(f"Unknown tier '{t}'. Valid: {list(TIER_SIZES)}")
    cfg = SciRetConfig(tier=t)
    cfg.ensure_dirs()
    return cfg


__all__ = [
    "SciRetConfig",
    "get_config",
    "TIER_SIZES",
    "CHUNK_SIZE_TOKENS",
    "CHUNK_OVERLAP_TOKENS",
    "MIN_TOKENS_PER_CHUNK",
    "BGE_M3_MODEL",
    "BGE_M3_DIM",
    "DPR_QUESTION_MODEL",
    "DPR_CONTEXT_MODEL",
    "DPR_DIM",
    "CROSS_ENCODER_MODEL",
    "CLIP_MODEL",
    "CLIP_DIM",
    "BLIP2_MODEL",
    "LLAVA_MODEL",
    "GEMINI_MODEL",
    "MISTRAL_MODEL",
    "DENSE_TOP_K",
    "SPARSE_TOP_K",
    "RRF_K",
    "RERANK_TOP_K",
    "SEED",
]
