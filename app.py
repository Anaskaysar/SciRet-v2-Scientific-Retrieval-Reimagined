import gradio as gr

def rag_pipeline(query):
    # Step 1: Retrieve top documents (replace with your logic)
    retrieved_docs = [
        {"title": "Paper 1", "score": 0.87, "content": "Sample content 1"},
        {"title": "Paper 2", "score": 0.82, "content": "Sample content 2"},
        {"title": "Paper 3", "score": 0.78, "content": "Sample content 3"},
    ]

    # Format retrieved docs
    retrieved_text = ""
    for i, doc in enumerate(retrieved_docs):
        retrieved_text += f"{i+1}. Title: {doc['title']}\n"
        retrieved_text += f"   Score: {doc['score']}\n"
        retrieved_text += f"   Content: {doc['content'][:200]}...\n\n"

    # Step 2: Generate answer (replace with LLM)
    answer = "Generated answer based on retrieved research papers."

    return retrieved_text, answer


iface = gr.Interface(
    fn=rag_pipeline,
    inputs=gr.Textbox(label="Enter your research question"),
    outputs=[
        gr.Textbox(label="Top Retrieved Papers"),
        gr.Textbox(label="Generated Answer")
    ],
    title="SciRet v2 — Scientific RAG System",
    description="Ask research questions and get answers with supporting papers"
)

if __name__ == "__main__":
    iface.launch()