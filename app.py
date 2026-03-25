import gradio as gr

def rag_pipeline(query, image):
    # Step 1: Retrieve top documents (dummy logic)
    retrieved_docs = [
        {"title": "Sample Paper A", "score": 0.91, "content": "This paper discusses multimodal RAG systems and early fusion techniques."},
        {"title": "Sample Paper B", "score": 0.85, "content": "Comparison of sparse and dense retrieval engines for scientific literature."},
        {"title": "Sample Paper C", "score": 0.79, "content": "Figure extraction techniques from scientific PDFs using LayoutLM and PyMuPDF."},
    ]

    # Format retrieved docs as styled HTML cards
    retrieved_html = "<div style='display:flex; flex-direction:column; gap:12px;'>"
    for i, doc in enumerate(retrieved_docs):
        retrieved_html += f"""
        <div style='border: 1px solid #0d6efd; padding: 15px; border-radius: 6px; background-color: #f8f9fa;'>
            <h4 style='margin-top:0; color:#0d6efd; font-family: sans-serif;'>{i+1}. {doc['title']} <span style='float:right; font-size: 0.85em; color:#dc3545; font-weight: normal;'>Score: {doc['score']}</span></h4>
            <p style='margin-bottom:0; color: #212529; font-size: 0.95em;'>{doc['content']}</p>
        </div>
        """
    retrieved_html += "</div>"
    
    # Step 2: Generate answer
    has_image = "and the provided visual context " if image is not None else ""
    answer = f"Based on the retrieved documents {has_image}addressing the query '{query}', multimodal RAG has been shown to improve understanding of complex scientific literature. (Dummy Output)"

    return retrieved_html, answer

# Customizing theme similar to the Bootstrap Primary/Dark style used in v1
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    button_primary_background_fill="*primary_600",
    button_primary_background_fill_hover="*primary_700",
    block_title_text_color="*primary_700",
    block_label_text_color="*primary_700",
)

with gr.Blocks(theme=custom_theme, title="SciRet v2", css="footer {visibility: hidden}") as iface:
    # Header Area
    gr.HTML("""
    <style>
        .sciret-header {
            text-align: center;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 15px 10px 15px;
        }
        .sciret-eyebrow {
            color: var(--color-accent, #0d6efd);
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 5px;
        }
        .sciret-logo {
            font-family: 'Libre Baskerville', serif;
            font-size: 2.8rem;
            color: var(--body-text-color, #212529);
            margin: 0 0 10px 0;
        }
        .sciret-logo .v2 {
            color: var(--color-accent, #0d6efd);
            font-size: 1.5rem;
            vertical-align: super;
        }
        .sciret-desc {
            color: var(--body-text-color-subdued, #495057);
            font-size: 1.15rem;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 25px;
        }
        .pill {
            background-color: var(--background-fill-secondary, #f8f9fa);
            color: var(--color-accent, #0d6efd);
            border: 1px solid var(--border-color-accent, #0d6efd);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .pill:hover {
            background-color: var(--color-accent, #0d6efd);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(13, 110, 253, 0.3);
        }
        .sciret-author {
            color: var(--body-text-color-subdued, #6c757d);
            font-size: 0.95rem;
        }
        .sciret-author a {
            color: var(--body-text-color, #212529);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s ease;
        }
        .sciret-author a:hover {
            color: var(--color-accent, #0d6efd);
        }
        .sciret-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--color-accent, #0d6efd), transparent);
            margin: 10px auto 30px auto;
            width: 70%;
            opacity: 0.5;
        }
    </style>
    <div class="sciret-header">
        <p class="sciret-eyebrow">Scientific Retrieval System</p>
        <h1 class="sciret-logo">SciRet <span class="v2">v2</span></h1>
        <p class="sciret-desc">
            Multimodal Retrieval-Augmented Generation for Scientific Knowledge Access —
            reasoning across text, figures, and tables in scientific literature.
        </p>
        <div class="pill-row">
            <span class="pill">BGE-M3</span>
            <span class="pill">CLIP</span>
            <span class="pill">BM25 + Dense</span>
            <span class="pill">Cross-Encoder Reranker</span>
            <span class="pill">Mistral 7B</span>
            <span class="pill">LLaVA</span>
            <span class="pill">RAGAS</span>
        </div>
        <p class="sciret-author">
            <a href="https://github.com/Anaskaysar">Kaysarul Anas Apurba</a>
            &nbsp;·&nbsp;
            <span style="color:var(--text-faint, var(--body-text-color-subdued));">MSc · Independent Researcher</span>
        </p>
    </div>
    <div class="sciret-divider"></div>
    """)
    
    with gr.Tabs(elem_id="main-tabs"):
        with gr.TabItem("Search Interface", id="tab-search"):
            gr.Markdown("<br>")
            with gr.Row():
                # LEFT COLUMN: Inputs
                with gr.Column(scale=1):
                    gr.Markdown("### 🔍 Input Query")
                    
                    with gr.Group():
                        query_input = gr.Textbox(
                            label="Natural Language Question",
                            placeholder="e.g. What imaging techniques were used to study COVID-19 lung damage?",
                            lines=3
                        )
                        image_input = gr.Image(
                            label="Optional Visual Query",
                            type="filepath",
                            height=250
                        )
                    
                    search_btn = gr.Button("Search", variant="primary", size="lg")
                
                # RIGHT COLUMN: Outputs
                with gr.Column(scale=2):
                    gr.Markdown("### ✨ Results")
                    
                    generated_answer = gr.Textbox(
                        label="Generated Answer",
                        lines=5,
                        interactive=False,
                        elem_classes=["answer-box"]
                    )
                    
                    gr.HTML("<hr style='border-color: #dee2e6; margin: 20px 0;'>")
                    gr.Markdown("### 📚 Top Retrieved Papers")
                    
                    retrieved_papers = gr.HTML(
                        label="Retrieved Context",
                        value="<div style='color: #6c757d; font-style: italic; padding: 20px; text-align: center; border: 1px dashed #ced4da; border-radius: 6px;'>No documents retrieved yet. Please run a search.</div>"
                    )
                    
            # Connect the search button
            search_btn.click(
                fn=rag_pipeline,
                inputs=[query_input, image_input],
                outputs=[retrieved_papers, generated_answer]
            )

        with gr.TabItem("About SciRet v2", id="tab-about"):
            gr.Markdown("""
            <div style="padding: 20px;">
                <h2 style="color: #0d6efd;">Overview</h2>
                <p style="font-size: 1.1em; line-height: 1.6;">
                Scientific papers are multimodal documents. A paper on COVID-19 lung imaging conveys critical information through 
                CT scan figures, comparison tables of patient outcomes, and statistical charts — not just through text. 
                A retrieval system that ignores these modalities is, by definition, incomplete.
                </p>
                <p style="font-size: 1.1em; line-height: 1.6;">
                <b>SciRet v2</b> addresses this gap by building a modern Retrieval-Augmented Generation (RAG) pipeline 
                that indexes and retrieves across all content types in scientific papers, then uses a vision-language model 
                to generate grounded, cited answers.
                </p>
                <hr style="margin: 30px 0; border-color: #dee2e6;">
                <h3 style="color: #212529;">Architecture Highlights</h3>
                <ul style="font-size: 1.05em; line-height: 1.8;">
                    <li><b>Hybrid Index</b>: Sparse (BM25) and Dense (ChromaDB) Reciprocal Rank Fusion</li>
                    <li><b>Multimodal Processing</b>: BGE-M3 for Text embeddings and CLIP/BLIP-2 for Visual embeddings</li>
                    <li><b>Generators</b>: Mistral 7B for text and LLaVA-7B for visual reasoning</li>
                    <li><b>Evaluation</b>: RAGAS Framework for end-to-end metrics</li>
                </ul>
            </div>
            """)

if __name__ == "__main__":
    iface.launch()