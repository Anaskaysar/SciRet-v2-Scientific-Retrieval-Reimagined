import os, pandas as pd
from dotenv import load_dotenv
load_dotenv()
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.run_config import RunConfig

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
base_dir = os.path.dirname(os.path.abspath(__file__)) # Assume running in evaluation dir
eval_path = os.path.join(base_dir, "..", "..", "4_results", "tier2", "eval_runs_tier2.parquet")

eval_df = pd.read_parquet(os.path.normpath(eval_path))
print(f"Loaded {len(eval_df)} eval runs")

tag_ragas_llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=GEMINI_KEY,
    convert_system_message_to_human=True,
    request_timeout=60
)
ragas_llm = LangchainLLMWrapper(tag_ragas_llm)
ragas_emb = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_KEY)
)
run_config = RunConfig(timeout=90, max_retries=3, max_workers=2)

# Small subset
ragas_results = {}
for sys_name in ["sciret_multi"]:
    subset = eval_df[eval_df["system"] == sys_name].head(2)
    ds = Dataset.from_dict({
        "question":     subset["question"].tolist(),
        "answer":       subset["answer"].tolist(),
        "contexts":     subset["contexts"].tolist(),
        "ground_truth": subset["ground_truth"].tolist(),
    })
    print(f"Evaluating {sys_name} (2 samples)...")
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy], llm=ragas_llm, embeddings=ragas_emb, run_config=run_config)
    print(f"Result: {result}")
