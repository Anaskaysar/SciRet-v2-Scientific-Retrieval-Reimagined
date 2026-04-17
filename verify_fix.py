import chromadb
import pydantic
import gradio
import os
import shutil

print(f"ChromaDB version: {chromadb.__version__}")
print(f"Pydantic version: {pydantic.__version__}")
print(f"Gradio version: {gradio.__version__}")

tmp_db_path = "./tmp_chroma_verify"
if os.path.exists(tmp_db_path):
    shutil.rmtree(tmp_db_path)

try:
    client = chromadb.PersistentClient(path=tmp_db_path)
    print("Successfully initialized chromadb.PersistentClient")
    collection = client.get_or_create_collection(name="test_collection")
    collection.add(
        documents=["This is a test document"],
        metadatas=[{"source": "test"}],
        ids=["id1"]
    )
    results = collection.query(
        query_texts=["This is a test document"],
        n_results=1
    )
    print(f"Query results: {results['ids']}")
    print("Successfully performed query on ChromaDB")
except Exception as e:
    print(f"Error during verification: {e}")
finally:
    if os.path.exists(tmp_db_path):
        shutil.rmtree(tmp_db_path)
