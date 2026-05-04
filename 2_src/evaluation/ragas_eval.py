import os, pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.run_config import RunConfig

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
print(f"Gemini: {'SET' if GEMINI_KEY else 'NOT SET'}")

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
eval_path = os.path.join(base_dir, "4_results", "tier2", "eval_runs_tier2.parquet")

eval_df = pd.read_parquet(eval_path)
print(f"Loaded {len(eval_df)} eval runs")
print(eval_df["system"].value_counts())

# ── RAGAS with Gemini ─────────────────────────────────────────────────────
tag_ragas_llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        google_api_key=GEMINI_KEY,
        convert_system_message_to_human=True,
        request_timeout=120
    )
ragas_llm = LangchainLLMWrapper(tag_ragas_llm)

run_config = RunConfig(timeout=180, max_retries=10, max_workers=2)
ragas_emb = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=GEMINI_KEY
    )
)

ragas_results = {}
for sys_name in ["dpr_baseline", "sciret_text", "sciret_multi"]:
    subset = eval_df[eval_df["system"] == sys_name].head(5)
    ds = Dataset.from_dict({
        "question":     subset["question"].tolist(),
        "answer":       subset["answer"].tolist(),
        "contexts":     subset["contexts"].tolist(),
        "ground_truth": subset["ground_truth"].tolist(),
    })
    try:
        result = evaluate(ds,
            metrics=[faithfulness, answer_relevancy,
                     context_precision, context_recall],
            llm=ragas_llm,
            embeddings=ragas_emb,
            run_config=run_config
        )
        ragas_results[sys_name] = dict(result)
        print(f"\n{sys_name}:")
        for k, v in dict(result).items():
            print(f"  {k}: {v:.3f}")
    except Exception as e:
        print(f"{sys_name} failed: {e}")

ragas_df = pd.DataFrame.from_dict(ragas_results, orient="index")
print("\n=== FINAL RAGAS RESULTS ===")
print(ragas_df.to_string())
output_path = os.path.join(base_dir, "4_results", "tier2", "ragas_tier2.csv")
ragas_df.to_csv(output_path)
print("\nSaved to ragas_tier2_fixed.csv")