const KEY = "phase0_todo_v1";
const groups = [
  {
    title: "Mathematics — Linear Algebra",
    items: [
      {
        t: "3Blue1Brown: Essence of Linear Algebra (all 15 videos)",
        s: "~3 hrs | youtube.com/3blue1brown",
        tag: "math",
      },
      {
        t: "Implement dot product & cosine similarity from scratch in NumPy",
        s: "no sklearn — write it yourself",
        tag: "math",
      },
      {
        t: "Implement matrix multiplication from scratch",
        s: "understand what is happening, not just np.dot()",
        tag: "math",
      },
      {
        t: "Read: what are eigenvalues and eigenvectors (intuition only)",
        s: "Wikipedia + 3B1B video 14",
        tag: "math",
      },
    ],
  },
  {
    title: "Mathematics — Calculus & Optimisation",
    items: [
      {
        t: "3Blue1Brown: Essence of Calculus (chapters 1-8)",
        s: "~3 hrs | focus on derivatives and chain rule",
        tag: "math",
      },
      {
        t: "3Blue1Brown: Neural Networks series (all 4 videos)",
        s: "~1 hr | backprop visualised perfectly",
        tag: "math",
      },
      {
        t: "Implement gradient descent on linear regression by hand",
        s: "no sklearn — just NumPy, plot the loss curve",
        tag: "math",
      },
    ],
  },
  {
    title: "Mathematics — Probability & Statistics",
    items: [
      {
        t: "Udemy Section 20: Getting Started With Statistics",
        s: "0/13 | 2hr 24min",
        tag: "udemy",
      },
      {
        t: "Udemy Section 21: Introduction To Probability",
        s: "0/2 | 22min",
        tag: "udemy",
      },
      {
        t: "Udemy Section 22: Probability Distribution Functions",
        s: "0/13 | 3hr",
        tag: "udemy",
      },
      {
        t: "Udemy Section 23: Inferential Statistics",
        s: "0/15 | 2hr 31min",
        tag: "udemy",
      },
      {
        t: "StatQuest: Bayes Theorem video",
        s: "~15 min | youtube StatQuest channel",
        tag: "free",
      },
      {
        t: "StatQuest: Maximum Likelihood Estimation video",
        s: "~15 min | StatQuest",
        tag: "free",
      },
      {
        t: "Write out cross-entropy loss formula and explain it in your own words",
        s: "H(y, ŷ) = -Σ y log(ŷ)",
        tag: "math",
      },
    ],
  },
  {
    title: "Machine Learning Foundations",
    items: [
      {
        t: "Udemy Section 27: Linear Regression In-Depth",
        s: "1/15 | 4hr 15min — gradient descent + cost function",
        tag: "udemy",
      },
      {
        t: "Udemy Section 30: Logistic Regression",
        s: "0/10 | 2hr 7min — classification + probability outputs",
        tag: "udemy",
      },
      {
        t: "Udemy Section 40: PCA",
        s: "0/6 | 1hr 29min — eigenvalues in real context",
        tag: "udemy",
      },
      {
        t: "Udemy Section 26: Introduction To Machine Learning",
        s: "5/5 done — just review your notes",
        tag: "udemy",
      },
    ],
  },
  {
    title: "Deep Learning & Neural Networks",
    items: [
      {
        t: "Udemy Section 52: Deep Learning",
        s: "0/39 | 6hr 44min — forward pass, backprop, activations",
        tag: "udemy",
      },
      {
        t: "Udemy Section 53: End to End Deep Learning Project (ANN)",
        s: "0/8 | 2hr 17min — hands-on solidifies theory",
        tag: "udemy",
      },
      {
        t: "Andrej Karpathy: Let's build GPT from scratch",
        s: "~2 hrs | single best transformer video — non-negotiable",
        tag: "free",
      },
    ],
  },
  {
    title: "Sequence Models → Transformers",
    items: [
      {
        t: "Udemy Section 55: Simple RNN In-Depth",
        s: "0/4 | 1hr 43min — understand why RNNs fail at long sequences",
        tag: "udemy",
      },
      {
        t: "Udemy Section 57: LSTM and GRU In-Depth",
        s: "0/8 | 2hr 6min — the fix for vanishing gradients",
        tag: "udemy",
      },
      {
        t: "Udemy Section 59: Bidirectional RNN",
        s: "0/1 | 23min — leads directly into BERT",
        tag: "udemy",
      },
      {
        t: "Udemy Section 60: Encoder-Decoder / Seq2Seq",
        s: "0/2 | 41min — foundation of RAG architecture",
        tag: "udemy",
      },
      {
        t: "Udemy Section 61: Attention Mechanism",
        s: "0/1 | 29min — the key idea before transformers",
        tag: "udemy",
      },
      {
        t: "Udemy Section 62: Transformers",
        s: "0/14 | 5hr 2min — most important section in the entire course",
        tag: "udemy",
      },
      {
        t: "Read paper: Attention Is All You Need (Vaswani et al. 2017)",
        s: "arxiv.org/abs/1706.03762 — read every section, derive the attention formula",
        tag: "free",
      },
    ],
  },
  {
    title: "NLP Foundations",
    items: [
      {
        t: "Udemy Section 51: NLP for Machine Learning",
        s: "0/34 | 6hr 25min — tokenisation, embeddings, text classification",
        tag: "udemy",
      },
      {
        t: "Udemy Section 54: NLP With Deep Learning",
        s: "0/1 | 18min — bridge from DL to NLP",
        tag: "udemy",
      },
      {
        t: "Read paper: BERT (Devlin et al. 2018)",
        s: "arxiv.org/abs/1810.04805 — understand pre-training objectives",
        tag: "free",
      },
      {
        t: "Read paper: Dense Passage Retrieval (Karpukhin et al. 2020)",
        s: "arxiv.org/abs/2004.04906 — you implemented this in 2022",
        tag: "free",
      },
      {
        t: "Read paper: RAG (Lewis et al. 2020)",
        s: "arxiv.org/abs/2005.11401 — your core framework",
        tag: "free",
      },
    ],
  },
  {
    title: "Computer Vision Foundations",
    items: [
      {
        t: "fast.ai Practical Deep Learning — Lesson 1 (CNNs)",
        s: "course.fast.ai — free, best practical intro to CNNs",
        tag: "free",
      },
      {
        t: "fast.ai Practical Deep Learning — Lesson 2",
        s: "course.fast.ai — transfer learning and fine-tuning",
        tag: "free",
      },
      {
        t: "Read paper: An Image is Worth 16x16 Words (ViT)",
        s: "arxiv.org/abs/2010.11929 — very readable, 30 min",
        tag: "free",
      },
      {
        t: "Read paper: CLIP (Radford et al. 2021)",
        s: "arxiv.org/abs/2103.00020 — your multimodal core",
        tag: "free",
      },
      {
        t: "Run CLIP demo: encode an image and a text query, compute cosine similarity",
        s: "HuggingFace transformers — 10 lines of code",
        tag: "free",
      },
    ],
  },
  {
    title: "Evaluation Metrics",
    items: [
      {
        t: "Derive and implement Recall@K from scratch",
        s: "write the formula, implement in Python, test on dummy data",
        tag: "math",
      },
      {
        t: "Derive and implement MRR (Mean Reciprocal Rank)",
        s: "MRR = (1/Q) × Σ 1/rank_i",
        tag: "math",
      },
      {
        t: "Understand NDCG formula and why it matters for ranking",
        s: "NDCG = DCG / IDCG — read the Wikipedia article",
        tag: "math",
      },
      {
        t: "Read RAGAS paper (Es et al. 2023)",
        s: "arxiv.org/abs/2309.15217 — your evaluation framework",
        tag: "free",
      },
    ],
  },
  {
    title: "Supplementary Free Courses",
    items: [
      {
        t: "DeepLearning.AI: LangChain for LLM Application Development",
        s: "deeplearning.ai — free, ~1.5 hrs, directly practical",
        tag: "free",
      },
      {
        t: "DeepLearning.AI: Building and Evaluating Advanced RAG",
        s: "deeplearning.ai — free, ~1 hr, covers hybrid search + reranking",
        tag: "free",
      },
      {
        t: "HuggingFace Course: Chapter on Transformers",
        s: "huggingface.co/learn — free, interactive notebooks",
        tag: "free",
      },
      {
        t: "HuggingFace Course: Chapter on Vision & Multimodal models",
        s: "huggingface.co/learn — free, covers CLIP and BLIP-2",
        tag: "free",
      },
      {
        t: "Stanford CS276 lecture notes: BM25 and evaluation metrics",
        s: "web.stanford.edu/class/cs276 — just the notes, no videos needed",
        tag: "free",
      },
    ],
  },
];

let state = {};
try {
  state = JSON.parse(localStorage.getItem(KEY) || "{}");
} catch (e) {}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {}
}

function updateStats() {
  let done = 0,
    total = 0;
  document.querySelectorAll(".task-item").forEach((el) => {
    total++;
    if (el.classList.contains("done")) done++;
  });
  document.getElementById("s-done").textContent = done;
  document.getElementById("s-total").textContent = total;
  document.getElementById("s-pct").textContent = total
    ? Math.round((done / total) * 100) + "%"
    : "0%";
  groups.forEach((g, gi) => {
    const items = g.items;
    const gdone = items.filter((_, ii) => state[gi + "_" + ii]).length;
    const bar = document.getElementById("bar_" + gi);
    const prog = document.getElementById("prog_" + gi);
    if (bar)
      bar.style.width = items.length
        ? Math.round((gdone / items.length) * 100) + "%"
        : "0%";
    if (prog) prog.textContent = gdone + "/" + items.length;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("lists");
  groups.forEach((g, gi) => {
    const card = document.createElement("div");
    card.className = "category-card";
    card.innerHTML = `
      <div class="category-header">
          <h2>${g.title}</h2>
          <span class="progress-info" id="prog_${gi}">0/${g.items.length}</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" id="bar_${gi}" style="width:0%"></div></div>
      <div class="task-list">
      ${g.items
        .map((item, ii) => {
          const id = gi + "_" + ii;
          const done = state[id] || false;
          const tagCol =
            item.tag === "udemy" ? "udemy" : item.tag === "math" ? "math" : "free";
          const tagText =
            item.tag === "udemy" ? "Udemy" : item.tag === "math" ? "Math" : "Free";
          return `<div class="task-item${
            done ? " done" : ""
          }" id="item_${id}" onclick="toggle('${id}')">
              <div class="checkbox${done ? " checked" : ""}" id="chk_${id}"></div>
              <div class="task-content">
                  <span class="badge ${tagCol}">${tagText}</span>
                  <div class="task-title">${item.t}</div>
                  <div class="task-sub">${item.s}</div>
              </div>
          </div>`;
        })
        .join("")}
      </div>`;
    container.appendChild(card);
  });

  window.toggle = function (id) {
    state[id] = !state[id];
    const el = document.getElementById("item_" + id);
    const chk = document.getElementById("chk_" + id);
    if (state[id]) {
      el.classList.add("done");
      chk.classList.add("checked");
    } else {
      el.classList.remove("done");
      chk.classList.remove("checked");
    }
    save();
    updateStats();
  };

  updateStats();
});
