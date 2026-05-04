import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- Configuration ---
TIER = "tier2"
RESULTS_DIR = os.path.join("4_results", TIER)
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- 1. Retrieval Recall Plot ---
def generate_recall_plot():
    df = pd.read_csv(os.path.join(RESULTS_DIR, "recall_at_k_tier2.csv"))
    
    # Identify k values
    ks = [1, 3, 5, 10, 20]
    methods = ["dense", "bm25", "hybrid"]
    
    # Aggregate means
    rows = []
    for k in ks:
        row = {"k": k}
        for m in methods:
            col = f"{m}_r{k}"
            if col in df.columns:
                row[m] = df[col].mean()
        rows.append(row)
    
    agg = pd.DataFrame(rows).set_index("k")
    
    fig, ax = plt.subplots(figsize=(7, 4))
    for col_, style in [("dense","-o"),("bm25","-s"),("hybrid","-^")]:
        if col_ in agg.columns:
            ax.plot(agg.index, agg[col_], style, label=col_)
    
    ax.set_xlabel("K"); ax.set_ylabel("Recall@K"); ax.set_ylim(0, 1.05)
    ax.set_title(f"Retrieval Recall@K — tier={TIER}")
    ax.legend(); ax.grid(True, ls=":")
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, "retrieval_recall_comparison.png")
    fig.savefig(plot_path, dpi=140)
    print(f"Generated {plot_path}")
    plt.close()

# --- 2. Reranking Precision Plot ---
def generate_precision_plot():
    df = pd.read_csv(os.path.join(RESULTS_DIR, "reranking_tier2.csv"))
    
    ks = [1, 3, 5, 10]
    rows = []
    for k in ks:
        rows.append({
            "k": k,
            "p_no_rerank": df[f"p_no_rerank_{k}"].mean(),
            "p_rerank": df[f"p_rerank_{k}"].mean()
        })
    
    agg = pd.DataFrame(rows).set_index("k")
    
    fig, ax = plt.subplots(figsize=(6, 3.5))
    x = np.arange(len(agg.index))
    ax.bar(x-0.2, agg["p_no_rerank"], 0.4, label="Stage 1 only (hybrid)", color="#64748b")
    ax.bar(x+0.2, agg["p_rerank"],    0.4, label="+ Cross-encoder rerank", color="#22c55e")
    ax.set_xticks(x); ax.set_xticklabels([f"P@{k}" for k in agg.index])
    ax.set_ylim(0, 1.05); ax.set_ylabel("Precision")
    ax.set_title(f"Precision@K — with vs without reranking (tier={TIER})")
    ax.legend()
    fig.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, "reranking_precision.png")
    fig.savefig(plot_path, dpi=140)
    print(f"Generated {plot_path}")
    plt.close()

# --- 3. Complementarity analysis (Simulated if indices missing, or from cached counts) ---
def generate_complementarity_plot():
    # Note: Full complementarity needs the actual retrieved IDs. 
    # If not available, we skip or use a placeholder if appropriate.
    # For now, let's skip as it's less critical than the main comparison plots.
    pass

# --- 4. Final Evaluation (RAGAS) Plot ---
def generate_ragas_plot():
    ragas_path = os.path.join(RESULTS_DIR, "ragas_tier2.csv")
    if not os.path.exists(ragas_path):
        print("RAGAS results not found. Skipping final evaluation plot.")
        return
        
    df = pd.read_csv(ragas_path, index_index=0)
    # Plotting logic for RAGAS metrics bar chart
    # ... logic from 09_evaluation ...
    pass

if __name__ == "__main__":
    generate_recall_plot()
    generate_precision_plot()
    # Placeholder for others as we finish RAGAS
