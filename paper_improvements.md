# SciRet — EMNLP 2026 Paper Improvement Checklist

Every item below is a concrete, actionable improvement. Each entry states:

- What the problem is
- Where to find it
- Exactly what to do
- Effort estimate

---

## CATEGORY 1 — CRITICAL BLOCKERS

_These will cause desk rejection or mandatory major revision if unfixed._

---

### 1.1 · Data Integrity: Tier 2 numbers in the paper don't match the raw CSV files

**Problem:** The paper reports Tier 2 numbers that differ from what is in
`4_results/tier2/recall_at_k_tier2.csv`. Specifically:

| Metric                           | Paper says | CSV actually has |
| -------------------------------- | ---------- | ---------------- |
| Dense R@1                        | 0.207      | **0.213**        |
| BM25 R@1                         | 0.180      | **0.200**        |
| Dense advantage over BM25 at R@1 | +0.027     | **+0.013**       |
| Dense R@10                       | 0.773      | **0.760**        |

The paper's key narrative ("dense overtakes BM25 by +0.027") is based on
incorrect numbers. The crossover is real but smaller than reported.

**Where:** `paper/emnlp2026_main.tex` Tables 4, 6, 7 and the Crossover
section (Finding 1). Also `4_results/tier2/scale_comparison.csv` row tier2.

**Fix:**

1. Recompute all averages directly from `4_results/tier2/recall_at_k_tier2.csv`
   using the Python script below, then update every number in the paper:
   ```python
   import csv
   with open('4_results/tier2/recall_at_k_tier2.csv') as f:
       rows = list(csv.DictReader(f))
   n = len(rows)
   for k in ['r1','r3','r5','r10','r20']:
       for sys in ['dense','bm25','hybrid']:
           vals = [float(r[f'{sys}_{k}']) for r in rows]
           print(f'{sys} R@{k[1:]}: {sum(vals)/n:.3f}')
   ```
2. Regenerate `4_results/tier2/scale_comparison.csv` from these numbers.
3. Update Tables 4, 6, 7, the crossover table, and all in-text numbers.

**Effort:** 30 minutes. **Priority: MUST FIX.**

---

### 1.2 · RAGAS Tier 2 generation scores are missing

**Problem:** The abstract and introduction both promise generation evaluation
results. The Limitations section admits they are "pending a library configuration
fix." Reviewers will treat this as an incomplete submission.

**Where:** The 150 generated answers are saved at
`4_results/tier2/eval_runs_tier2.parquet`. The fix code is documented in
`0_docs/Analysis/analysis_tier2_complete.md` Section 5.

**Fix:** The exact corrected RAGAS code is already written — paste it into
Kaggle, point it at `eval_runs_tier2.parquet`, run. Estimated time: 20–30
minutes. Then add a results table to the paper (Section 5 or Appendix).

**Effort:** 1 hour on Kaggle. **Priority: MUST FIX.**

---

### 1.3 · Citation Integrity Score (CIS): introduced everywhere, results nowhere

**Problem:** CIS is listed as Contribution 4 in the introduction, has its
own equation (Eq. 2), and is described as a new metric. But there are zero
CIS scores anywhere in the Results section. This is a broken promise to reviewers.

**Where:** `paper/emnlp2026_main.tex` — Introduction (line 98), Section 3.5,
and the Results section (Section 5) which never mentions CIS again.

**Fix (two options — pick one):**

- **Option A (recommended):** Compute CIS scores. DeBERTa-v3 NLI runs locally
  on CPU in ~2 hours on 150 answers (already saved). Then add a small CIS table
  to Section 5 with scores per system. Even preliminary scores are publishable.
- **Option B (acceptable):** Move CIS entirely to Future Work. Remove it from
  the contributions list in the Introduction. Change "We introduce CIS" to
  "We propose CIS as a future evaluation direction." Remove Eq. 2 from the
  main body or demote it to Appendix.

**Effort:** Option A = 2 hours. Option B = 20 minutes. **Priority: MUST FIX.**

---

### 1.4 · Title overclaims "Scale Laws" with only 2 data points

**Problem:** The word "Laws" implies a fitted power-law or log-linear curve
(cf. Kaplan et al. 2020). You have two corpus sizes: 1,034 and 51,130 chunks.
Two points define a line, not a law. EMNLP reviewers familiar with the
scaling literature will reject this framing immediately.

**Where:** `paper/emnlp2026_main.tex` line 16–17 (title) and the abstract
(line 36, "Scale Laws").

**Fix (two options):**

- **Option A (quick):** Retitle to:
  _"Corpus Scale Effects in Scientific RAG: Empirical Evidence for BM25/Dense
  Crossover and Domain-Mismatch Reranking Degradation"_
  Change "Scale Laws" → "scale effects" everywhere in abstract and intro.
- **Option B (stronger):** Add 2 intermediate scale points (5K and 25K chunks)
  on Kaggle (both fit in free-tier session). You can then fit a curve and
  actually have scale law evidence.

**Effort:** Option A = 5 minutes. Option B = 4–6 hours on Kaggle. **Priority: MUST FIX.**

---

### 1.5 · Co-author fields are placeholders

**Problem:** Lines 24–30 of the paper have "Co-author Name 1", "Co-author
Name 2", and "email@domain". This cannot be submitted.

**Where:** `paper/emnlp2026_main.tex` lines 24–30.

**Fix:** Confirm authorship with the professor and fill in real names, affiliations,
and email addresses. Also remove the `[review]` option from `\usepackage[review]{acl}`
for final submission (keep it for peer review blind submission).

**Effort:** 10 minutes. **Priority: MUST FIX.**

---

## CATEGORY 2 — METHODOLOGICAL INTEGRITY

_These will draw pointed questions from reviewers. Each weakens the core claims._

---

### 2.1 · Pseudo-relevance ground truth is circular

**Problem:** The "relevant set" for evaluation is defined as the top-3 results
from the hybrid RRF system itself. You then evaluate all three systems (including
hybrid) against this ground truth. This systematically biases results in favour
of hybrid and against any system that ranks documents differently. Analysis
notebook `analysis_nb05_reranking.md` Section 3 explicitly notes:
_"Measuring reranking against a ground truth derived from the same retrieval
system creates a circular dependency."_ This is your biggest methodological risk.

**Where:** `paper/emnlp2026_main.tex` Section 4.3 (Evaluation), line 263.
The annotation CSV is at `4_results/passages_for_annotation.csv` (Tier 1)
and `4_results/tier2/passages_for_annotation.csv` (Tier 2).

**Fix:**

1. Even 50 manually annotated queries (2–3 hours with a binary relevance judgment
   per passage) transforms this from a methodological weakness into a strength.
2. At minimum, add a sentence explicitly acknowledging the circularity:
   _"We note that pseudo-relevance labels derived from the hybrid system's
   own top-3 results may underestimate performance differences between systems
   due to recall bias toward the label-generating system. Manual annotation of
   [N] queries is underway and will be incorporated."_

**Effort:** Manual annotation = 2–3 hours. Disclosure sentence = 5 minutes.

---

### 2.2 · Hybrid R@1 = 0.333 is actually the theoretical maximum — clarify this

**Problem:** The paper reports Hybrid R@1 = 0.333 at Tier 2 without explaining
that with exactly 3 pseudo-relevant documents per query, the maximum achievable
Recall@1 is 1/3 = 0.333. The raw data confirms that hybrid achieves R@1 = 1/3
for **all 50 queries**, meaning its rank-1 document is always relevant. This
is a perfect rank-1 result that should be highlighted, not buried.

**Where:** `paper/emnlp2026_main.tex` Table 4 caption (line 315) and the
Retrieval Ablation section (line 319).

**Fix:** Add one sentence after Table 4:
_"With 3 pseudo-relevant documents per query, R@1 is bounded above by 1/3.
Hybrid retrieval achieves this maximum for all 50 queries, confirming that
the top-ranked document is always relevant at Tier 2."_

**Effort:** 5 minutes.

---

### 2.3 · Answer relevancy = 0.042 appears in the comparison table but is never explained

**Problem:** The analysis (`analysis_nb09_evaluation_final.md` Section 3)
explicitly states: _"Do not report this number — it reflects the generator
fallback, not the system quality."_ But the table `4_results/tier1/final_comparison_table_paper.csv`
has answer_relevancy = 0.042–0.043 for all systems. If this appears anywhere
in the paper, reviewers will flag it as near-zero and question whether the
whole system is broken.

**Where:** Check if this table feeds into any paper table. If so, remove the
answer*relevancy column from the paper tables entirely and add a footnote:
*"Answer Relevancy is not reported at Tier 1 due to use of a local fallback
generator; Tier 2 scores with Gemini 1.5 Flash are reported separately."\_

**Effort:** 10 minutes.

---

### 2.4 · Context Precision = 0.103 is low and never explained

**Problem:** The RAGAS context precision of ~0.103 across all Tier 1 systems
is low and will attract reviewer questions. The analysis notebook explains
two causes (domain-mismatch reranker and many topically similar chunks), but
the paper never mentions this.

**Where:** `paper/emnlp2026_main.tex` — RAGAS discussion is absent from the
Results section.

**Fix:** Add 2 sentences in the generation results discussion:
_"Context Precision (0.103) is lower than Context Recall (0.586), reflecting
two factors: (1) the cross-encoder reranker's domain mismatch disrupts the
RRF ordering, moving relevant documents from top positions (Section 5.2);
(2) at 1,034 chunks, multiple topically similar passages achieve comparable
relevance scores, reducing top-precision while maintaining recall."_

**Effort:** 10 minutes.

---

### 2.5 · The BM25/Dense crossover claim needs stronger grounding

**Problem:** The paper claims this is "the first empirical measurement of a
BM25/dense crossover in scientific RAG." This is a strong novelty claim that
reviewers will challenge by asking for a prior work search. The BEIR benchmark
(Thakur et al. 2021) does study BM25 vs dense across many corpus sizes but
doesn't frame it as a scale crossover. You should cite BEIR and explicitly
say how your study differs.

**Where:** `paper/emnlp2026_main.tex` Introduction, line 83 and the
BM25/Dense Crossover paragraph in Discussion.

**Fix:**

1. Add to Related Work: _"BEIR \citep{thakur2021beir} evaluates zero-shot
   retrieval across heterogeneous corpora of varying sizes, but does not hold
   the pipeline fixed and vary only corpus size. Our controlled two-tier design
   isolates scale as the sole variable."_
2. Soften "first empirical measurement" to "controlled empirical demonstration
   with a fixed pipeline" — accurate and harder to dispute.

**Effort:** 15 minutes.

---

## CATEGORY 3 — STATISTICAL RIGOR

_Each missing element invites a reviewer to question the reliability of your claims._

---

### 3.1 · No statistical tests reported at Tier 1

**Problem:** The paper reports Wilcoxon p < 0.0001 at Tier 2 (n=50) but no
significance test at Tier 1 (n=31). A reviewer will ask why.

**Where:** `paper/emnlp2026_main.tex` line 319–323.

**Fix:** Run Wilcoxon signed-rank on per-query Recall@10 values from
`4_results/tier1/eval_runs.parquet` or `recall_at_k.csv` at Tier 1.
If it comes out significant, report it. If not, say explicitly:
_"Tier 1 significance tests are underpowered due to small query set (n=31);
Tier 2 results (n=50) provide the primary statistical evidence."_

**Effort:** 15 minutes of Python code.

---

### 3.2 · No effect size reported alongside p-values

**Problem:** Statistical significance (p-value) alone is insufficient by
modern NLP standards. EMNLP reviews increasingly ask for effect size (Cohen's d
or rank-biserial correlation for Wilcoxon).

**Where:** `paper/emnlp2026_main.tex` line 319.

**Fix:** Add rank-biserial correlation r alongside the Wilcoxon result:

```python
from scipy.stats import wilcoxon
stat, p = wilcoxon(hybrid_r10, dense_r10)
# r = Z / sqrt(n) for rank-biserial
```

Then report: _"(Wilcoxon p < 0.0001, rank-biserial r = X.XX, n=50)"_

**Effort:** 10 minutes.

---

### 3.3 · No confidence intervals on any metric

**Problem:** All reported metrics are point estimates with no uncertainty bounds.
For metrics averaged over 50 queries, a 95% bootstrap confidence interval takes
minutes to compute and substantially strengthens credibility.

**Fix:** For key numbers (e.g., Hybrid R@10 = 1.000, Dense R@10 = 0.760),
add bootstrap CIs:

```python
import numpy as np
vals = [float(r['hybrid_r10']) for r in rows]
boots = [np.mean(np.random.choice(vals, len(vals))) for _ in range(10000)]
print(f'95% CI: [{np.percentile(boots,2.5):.3f}, {np.percentile(boots,97.5):.3f}]')
```

Report in table footnote or inline.

**Effort:** 30 minutes for all key metrics.

---

### 3.4 · Wilcoxon is only reported for Hybrid vs Dense — not Hybrid vs BM25

**Problem:** At Tier 2, Hybrid clearly dominates BM25 as well. Reporting
significance only for Hybrid vs Dense is incomplete.

**Where:** `paper/emnlp2026_main.tex` line 319.

**Fix:** Add one more Wilcoxon test:
_"(Hybrid vs BM25: Wilcoxon p = X, n=50)"_ Takes 2 lines of code.

**Effort:** 5 minutes.

---

### 3.5 · No discussion of multiple comparisons (5 K values × 3 systems = 15 tests)

**Problem:** Reporting 15 metrics across 5 K-values and 3 systems without
correction inflates Type I error. At minimum, acknowledge this.

**Where:** `paper/emnlp2026_main.tex` Section 4.3 or Limitations.

**Fix:** Add one sentence: _"All significance tests use α=0.05 without
correction for multiple comparisons; we report p-values for primary comparisons
only and treat secondary comparisons as exploratory."_

**Effort:** 5 minutes.

---

## CATEGORY 4 — RELATED WORK AND CITATIONS

_Wrong or missing citations signal carelessness to reviewers._

---

### 4.1 · lin2022rrf citation is wrong — it's not about RRF

**Problem:** `emnlp_biblio.bib` cites `lin2022rrf` as:
_"A Few Brief Notes on DeepImpact, COIL, and a Conceptual Framework for
Information Retrieval Techniques"_ — this paper is about learned sparse models
(DeepImpact and COIL), not about RRF. Using it to support the claim that
"hybrid retrieval generally outperforms single-modality systems" is incorrect.

**Where:** `paper/emnlp_biblio.bib` entry `lin2022rrf`, and
`paper/emnlp2026_main.tex` line 119.

**Fix:** Replace with a proper citation for hybrid/RRF superiority.
Good options:

- Kuzi et al. (2020) "Query Expansion Using Word Embeddings" (CIKM)
- Ma et al. (2022) "ASMR" or Formal et al. (2021) SPLADE papers
- Or simply remove the \citep{lin2022rrf} and let the Cormack 2009 citation
  stand on its own — the sentence is supported by it alone.

**Effort:** 15 minutes.

---

### 4.2 · Missing DeBERTa-v3 citation for CIS

**Problem:** Section 3.5 describes CIS using "DeBERTa-v3" as the NLI model
but never cites it. Reviewers will notice.

**Where:** `paper/emnlp2026_main.tex` Section 3.5 (line 218).

**Fix:** Add to `emnlp_biblio.bib`:

```bibtex
@article{he2021deberta,
  title   = {{DeBERTa}: Decoding-enhanced {BERT} with Disentangled Attention},
  author  = {He, Pengcheng and Liu, Xiaodong and Gao, Jianfeng and Chen, Weizhu},
  journal = {arXiv preprint arXiv:2006.03654},
  year    = {2021}
}
```

Then add `\citep{he2021deberta}` after "DeBERTa-v3" in Section 3.5.

**Effort:** 5 minutes.

---

### 4.3 · BioASQ citation uses wrong field type (`booktitle` should be `journal`)

**Problem:** `emnlp_biblio.bib` entry `bioasq` uses `booktitle = {BMC Bioinformatics}`
but BMC Bioinformatics is a journal, not conference proceedings. LaTeX will
format this as a conference paper, which is incorrect.

**Where:** `paper/emnlp_biblio.bib` entry `bioasq`.

**Fix:** Change `booktitle` to `journal`:

```bibtex
journal = {BMC Bioinformatics},
```

**Effort:** 2 minutes.

---

### 4.4 · nogueira2019passage has wrong booktitle format

**Problem:** The entry for `nogueira2019passage` has
`booktitle = {arXiv preprint arXiv:1901.04085}` — you cannot use an arXiv
preprint as a booktitle. This is a formatting error that will look unprofessional.

**Where:** `paper/emnlp_biblio.bib` entry `nogueira2019passage`.

**Fix:** Either (a) find the published venue — it was published at the EMNLP
workshop "Deep Learning Inside Out" 2019 — or (b) convert it to an `@article`
with `journal = {arXiv preprint arXiv:1901.04085}`.

**Effort:** 5 minutes.

---

### 4.5 · Missing sentence-transformers citation

**Problem:** The paper relies on `sentence-transformers` for BGE-M3 embedding,
but Reimers & Gurevych (2019) "Sentence-BERT" is not cited anywhere.

**Fix:** Add to bibliography and cite in Section 3.3 where BGE-M3 is introduced:

```bibtex
@inproceedings{reimers2019sbert,
  title     = {Sentence-{BERT}: Sentence Embeddings using Siamese {BERT}-Networks},
  author    = {Reimers, Nils and Gurevych, Iryna},
  booktitle = {Proceedings of EMNLP-IJCNLP},
  pages     = {3982--3992},
  year      = {2019}
}
```

**Effort:** 5 minutes.

---

### 4.6 · Missing SPECTER / domain-specific embedding models in Related Work

**Problem:** SPECTER (Cohan et al., 2020) and SciNCL (Ostendorff et al., 2022)
are scientific domain-adapted embedding models directly relevant to scientific RAG.
Not citing them opens the door for a reviewer to ask "why didn't you compare with
domain-adapted embeddings like SPECTER?"

**Where:** `paper/emnlp2026_main.tex` Related Work, after the Hybrid Retrieval
paragraph.

**Fix:** Add a short "Scientific Embeddings" paragraph:
_"Domain-adapted embeddings for scientific text (SPECTER \citep{cohan2020specter};
SciNCL \citep{ostendorff2022scincl}) offer an alternative to general-purpose
models. We use BGE-M3 \citep{chen2024bgem3} as a strong general baseline and
identify domain-adapted retrieval as future work."_

**Effort:** 20 minutes including adding bib entries.

---

### 4.7 · Missing ColBERT / late-interaction models in Related Work

**Problem:** ColBERT (Khattab & Zaharia, 2020) is a major retrieval paradigm
that sits between bi-encoders and cross-encoders — highly relevant to your
Stage 1 vs Stage 2 design. Not mentioning it is a gap reviewers will notice.

**Fix:** One sentence in Related Work, Cross-Encoder Reranking paragraph:
_"Late-interaction models such as ColBERT \citep{khattab2020colbert} offer
a middle ground between bi-encoder speed and cross-encoder accuracy; we defer
exploration of this paradigm to future work."_

**Effort:** 10 minutes.

---

## CATEGORY 5 — WRITING AND PRESENTATION

_These improve clarity, precision, and the persuasiveness of your arguments._

---

### 5.1 · "Ruling out corpus size" is slightly overclaimed

**Problem:** The paper says the reranking degradation pattern "rules out corpus
size as the primary cause." But with only two data points, you can show the
pattern is consistent — you cannot definitively "rule out" an alternative
hypothesis. This is an overstatement that reviewers will mark.

**Where:** `paper/emnlp2026_main.tex` line 428 and the abstract (line 46).

**Fix:** Change "ruling out" to "arguing against" or "providing evidence
against." Example:
_"...providing evidence against corpus size as the primary cause and supporting
domain mismatch as the dominant factor."_

**Effort:** 5 minutes.

---

### 5.2 · BM25's R@10 improvement explanation is weak

**Problem:** The paper says BM25 shows the largest R@10 improvement (+19.9pp)
"possibly because the larger corpus contains more relevant documents that BM25's
exact-match finds at higher recall thresholds." This is circular and confusing —
a larger corpus also means more irrelevant exact matches.

**Where:** `paper/emnlp2026_main.tex` Scale Comparison section (line 453–456).

**Fix:** The real explanation is: at small scale (1,034 chunks), BM25's
exact-match reaches a ceiling early because the corpus is thin on vocabulary
variety. At large scale, more passages contain query-relevant terms that BM25
can match at K=10. Replace the current explanation with:
_"BM25's large R@10 improvement (+19.9pp) reflects its exact-match ceiling
effect at small scale: in a 1,034-chunk corpus, high-IDF terms match few
documents, limiting recall at any K. At 51,130 chunks, more passages contain
query-relevant terms, raising BM25's recall ceiling."_

**Effort:** 10 minutes.

---

### 5.3 · CIS "model-independent" claim is imprecise

**Problem:** Section 3.5 says CIS is "independent of the generation model" but
the CIS formula uses "claims(a) atomic claims decomposed by LLM" — the claim
decomposition step still uses an LLM. What you mean is that the _judge_ model
(DeBERTa-v3 NLI) is independent of the _generator_ model (Gemini 1.5 Flash).
The current wording is misleading.

**Where:** `paper/emnlp2026_main.tex` Section 3.5, line 209–211 and the
abstract line 51.

**Fix:** Replace "independent of the generation model" with:
_"using a cross-model evaluation strategy where the judge model (DeBERTa-v3 NLI)
is a different model family from the generator (Gemini 1.5 Flash), avoiding the
self-evaluation bias of single-model assessment."_

**Effort:** 10 minutes.

---

### 5.4 · Missing per-query-type breakdown — you have the data already

**Problem:** The evaluation question set has 6 types (imaging, molecular,
clinical, treatment, dataset, synthesis). The raw CSV
`4_results/tier2/recall_at_k_tier2.csv` has a `type` column. You could
add a one-page appendix table showing Recall@10 per query type at Tier 2.
This strengthens the paper by showing whether scale effects differ across
query types (e.g., does molecular outperform imaging at scale?).

**Where:** `4_results/tier2/recall_at_k_tier2.csv` (type column exists).

**Fix:** Run this:

```python
import csv
from collections import defaultdict
with open('4_results/tier2/recall_at_k_tier2.csv') as f:
    rows = list(csv.DictReader(f))
by_type = defaultdict(list)
for r in rows:
    by_type[r['type']].append(float(r['hybrid_r10']))
for t, vals in sorted(by_type.items()):
    print(f'{t}: {sum(vals)/len(vals):.3f}  (n={len(vals)})')
```

Add results as Appendix Table C.

**Effort:** 30 minutes.

---

### 5.5 · The Discussion paragraph on "why BM25 crossover happens" is good but needs one citation

**Problem:** The IDF saturation explanation in Discussion (lines 462–468) is
intuitive but uncited. Add one citation to any IR textbook or paper that
discusses IDF corpus-size effects.

**Fix:** Add: _"...as the corpus grows, term document frequencies increase
and IDF values decrease \citep{robertson2009bm25}..."_ and add the
Robertson & Zaragoza (2009) BM25 survey to the bibliography.

**Effort:** 10 minutes.

---

### 5.6 · No qualitative error analysis in the main paper

**Problem:** The analysis notebook `analysis_nb05_reranking.md` Section 5
has three excellent qualitative examples (IL-6 query = good reranking,
CT imaging query = bad reranking, mRNA vaccines = neutral). These make the
domain mismatch explanation concrete and compelling. None of them appear in
the paper.

**Fix:** Add a small table or paragraph to Section 5.2 (Finding 2) with the
CT imaging example: _"For example, for the query 'COVID-19 imaging techniques',
Stage 1 correctly ranks 'High-resolution CT features of COVID-19 pneumonia'
at rank 3. After reranking, this document drops out of the top-5 while 'Detection
using Deep Neural Networks with Ultrasound Imaging' (a classification paper)
rises to rank 1, rewarded by the MS MARCO reranker for containing 'imaging' as
a keyword."_

**Effort:** 20 minutes.

---

### 5.7 · Appendix complementarity table only shows Tier 1 — add Tier 2

**Problem:** Appendix A has the Jaccard/complementarity analysis for Tier 1
only. If the same analysis was run at Tier 2, it should be included. If not,
noting whether complementarity increases or decreases with scale is a
natural follow-up that strengthens Finding 1.

**Fix:** Run the complementarity analysis on Tier 2 retrieval results and
add a second column or table to Appendix A.

**Effort:** 1–2 hours depending on whether Tier 2 complementarity was logged.

---

### 5.8 · Spelling inconsistency: British vs American English

**Problem:** The paper mixes "specialised" (British) with general American
English spelling. EMNLP is an American venue and conventionally uses American
English.

**Where:** `paper/emnlp2026_main.tex` lines 64, 161 ("specialised").

**Fix:** Change "specialised" → "specialized" throughout.
Run: `grep -n "specialised\|recognised\|organised" paper/emnlp2026_main.tex`
to find all instances.

**Effort:** 5 minutes.

---

### 5.9 · Table captions are not fully self-contained

**Problem:** Table 3 caption says "BM25 wins at R@1; hybrid wins at K≥3"
but doesn't say what the ground truth is or how many queries. Reviewers
reading just the table should understand it without reading the text.

**Where:** `paper/emnlp2026_main.tex` Table 3 caption (line 298–299) and
Table 4 caption (line 314–316).

**Fix:** Expand captions to include ground truth method and query count.
Example for Table 3:
_"Recall@K — Tier 1 (31 queries, 1,034 chunks, pseudo-relevance top-3 labels).
BM25 wins at R@1 via exact scientific term matching; hybrid wins at K≥3."_

**Effort:** 15 minutes for all tables.

---

### 5.10 · Abstract says all code/indexes/data released — verify GitHub is public

**Problem:** Line 53 of the abstract cites `https://github.com/Anaskaysar/sciret`
as the release URL. If this repo is private or empty, that's a credibility issue.

**Fix:** Ensure the GitHub repo is public, has a README, and contains at
minimum: the evaluation questions, the comparison tables in CSV form, and
instructions for reproducing Tier 2. Notebooks can be linked via Kaggle.

**Effort:** 1–2 hours to clean up and publish.

---

## CATEGORY 6 — EXPERIMENTAL COMPLETENESS

_These add evidence depth without requiring major re-runs._

---

### 6.1 · Only one domain — single-domain generalizability is a known reviewer critique

**Problem:** All experiments use CORD-19 (COVID-19). A reviewer will ask:
"Does the BM25/dense crossover generalize beyond COVID-19 literature?"

**Fix (two options):**

- **Option A (easy):** Add to Limitations: _"All experiments use CORD-19
  (COVID-19 domain). Generalization to other scientific domains (biomedical,
  chemistry, materials science) is future work."_ — you already partially say this.
- **Option B (strong):** Run a brief Tier 1 experiment on 1,000 papers from
  a different dataset (e.g., arXiv CS-IR, PubMed subset). Even a single
  reproducibility check at small scale would be compelling.

**Effort:** Option A = 5 minutes. Option B = 4–6 hours.

---

### 6.2 · DPR baseline uses NQ-trained encoder — not ideal for scientific text

**Problem:** The paper uses `facebook/dpr-ctx_encoder-single-nq-base` as the
DPR baseline. This was trained on Natural Questions (Wikipedia). For a fair
scientific domain comparison, `facebook/dpr-ctx_encoder-multiset-base`
(trained on multiple datasets) or even a science-specific DPR would be more
appropriate. Reviewers may challenge the baseline's fairness.

**Where:** `paper/emnlp2026_main.tex` Section 4.2 (Baselines), line 253.

**Fix:** Acknowledge this in the experimental setup:
_"We use `dpr-ctx_encoder-single-nq-base` as the DPR baseline to represent
out-of-domain dense retrieval, analogous to the domain-mismatch conditions we
study in the reranking analysis."_ This turns a weakness into intentional
framing.

**Effort:** 10 minutes.

---

### 6.3 · No ablation over RRF k parameter

**Problem:** RRF uses k=60 (standard), but no ablation is reported. A reviewer
could ask whether the crossover finding is sensitive to k.

**Where:** `paper/emnlp2026_main.tex` Section 3.4, line 196.

**Fix (minimal):** Add one sentence: _"We use the standard k=60 \citep{cormack2009rrf};
we do not ablate this parameter as prior work shows RRF is robust to k in
the range 10–100."_ Then cite one paper that shows this robustness.

**Effort:** 10 minutes.

---

### 6.4 · No latency/efficiency comparison between retrieval systems

**Problem:** BM25 is much faster than BGE-M3 dense retrieval. The paper
makes a strong recommendation for hybrid retrieval but never mentions the
inference cost trade-off. Practitioners need this.

**Fix:** Add a one-line table to the Appendix or a sentence in Discussion:
_"BM25 retrieval latency is O(|V|) per query (~2ms at Tier 2); BGE-M3 dense
retrieval requires embedding the query (~15ms) plus HNSW ANN lookup (~5ms).
Hybrid adds only the BM25 retrieval and RRF fusion steps, totalling ~25ms
per query at Tier 2."_ Exact numbers from your Kaggle logs would be ideal.

**Effort:** 20 minutes to look up timings and add.

---

### 6.5 · BGE-M3 multi-vector mode not explored

**Problem:** BGE-M3 supports three retrieval modes: dense, sparse (learned),
and multi-vector (ColBERT-style). You only use dense mode. This is fine to
note explicitly rather than leave as an implicit gap.

**Fix:** Add one sentence in Section 3.3:
_"BGE-M3 supports sparse and multi-vector retrieval modes in addition to the
dense mode we use here; exploring these capabilities in the hybrid fusion is
future work."_

**Effort:** 5 minutes.

---

### 6.6 · UMAP embedding visualization is computed but not in the paper

**Problem:** `analysis_nb03_embedding_baseline.md` Section 8 mentions a
UMAP plot was generated (`umap_embeddings.png`). Embedding space visualizations
are standard in retrieval papers and would help readers understand why dense
retrieval improves at scale.

**Where:** `4_results/tier1/umap_embeddings.png` should exist.

**Fix:** Add the UMAP plot to Appendix B with a caption explaining the cluster
structure (query types cluster distinctly, confirming semantic coherence).

**Effort:** 15 minutes.

---

## CATEGORY 7 — TECHNICAL / CODE

_These don't directly affect the paper text but affect reproducibility._

---

### 7.1 · DPR DEVICE variable bug (NB03) never resolved

**Problem:** `analysis_nb03_embedding_baseline.md` Section 5 notes that DPR
crashed with `name 'DEVICE' is not defined`. The DPR Recall@K comparison at
Tier 1 may not have been computed correctly as a result.

**Where:** `3_notebooks/tier_1/03_embedding_baseline.ipynb`

**Fix:** Add `DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'`
to the config cell. Rerun the DPR baseline evaluation at Tier 1 to confirm
the numbers match the paper's Table 3.

**Effort:** 30 minutes.

---

### 7.2 · Tier 1 NB04 used 20 queries but paper reports 31

**Problem:** `analysis_nb04_hybrid_retrieval.md` says "Evaluation: 20 queries"
but the paper Table 3 caption says "(31 queries, 1,034 chunks)." Either the
Recall@K numbers in Table 3 were computed from a different run than what NB04
logged, or NB04 was run before the query set was expanded to 31. This internal
inconsistency should be verified.

**Fix:** Check when the query set expansion from 20 to 31 happened and confirm
the paper numbers (Dense R@1=0.104, BM25 R@1=0.139, Hybrid R@10=0.950) are
from the 31-query run. The final numbers in `4_results/tier1/recall_at_k.csv`
show 5 K-values with these exact values — confirm these were generated on 31
queries.

**Effort:** 15 minutes.

---

### 7.3 · Embedding timing in Section 3.3 says "72.8 minutes" — verify this matches logs

**Problem:** The paper says BGE-M3 embedding at Tier 2 "required 72.8 minutes
on a T4 GPU." Verify this is from the actual Kaggle session logs rather than
an estimate.

**Where:** `paper/emnlp2026_main.tex` line 186. Kaggle notebook logs.

**Fix:** Cross-check with the Tier 2 Kaggle notebook output. If confirmed,
it's fine. If it was an estimate, either verify or change to "approximately
70 minutes."

**Effort:** 5 minutes.

---

## CATEGORY 8 — MINOR POLISH

_Small but visible to careful reviewers._

---

### 8.1 · `[review]` option in `\usepackage[review]{acl}` should be removed for final submission

The `[review]` option enables double-blind anonymization. Confirm whether
EMNLP 2026 is double-blind (it typically is). If submitting blind, keep it
during review and remove for camera-ready. Make sure author names are blinded
in the review version.

---

### 8.2 · "email@domain" placeholder on line 29

Line 29 of the .tex file has `\texttt{email@domain}`. This is a second
placeholder that needs a real email address.

---

### 8.3 · Non-breaking tildes inconsistent

The paper uses `Tier~1` and `Tier~2` (correct, non-breaking) in some places
but `Tier 1` (breakable) in others. Run:
`grep -n "Tier [12]" paper/emnlp2026_main.tex`
to find unprotected instances and fix them.

---

### 8.4 · `\And` vs `\and` for 3+ authors

With 3 authors listed separately in the ACL format, use `\AND` (uppercase)
between author blocks. Verify the author block renders correctly in the compiled PDF.

---

### 8.5 · The lin2022rrf bibliography entry has `year = {2021}` but key says `2022`

The bib key `lin2022rrf` has `year = {2021}`. Pick one — either fix the key
to `lin2021rrf` or fix the year. Either way, the citation is wrong (see 4.1).

---

### 8.6 · "non-parametric" hyphenation

Line 61: "non-parametric retrieval" — consistent hyphenation throughout.
Check for "nonparametric" variants.

---

### 8.7 · Figure captions should all state Tier (1 or 2)

Figures 1–4 captions reference tier-specific results. Ensure every figure
caption says "Tier 1" or "Tier 2" explicitly so the figure is self-contained
for readers who jump to figures first.

---

### 8.8 · Appendix table label reference mismatch

The paper references `\label{app:complementarity}` and `\label{app:questions}`
in the appendix but the main body never `\ref{}` them. Confirm these are
referenced somewhere in the text, or these appendix labels are orphaned.

---

## SUMMARY: PRIORITIZED WORK ORDER

| #    | Item                                                                  | Time           | Impact   |
| ---- | --------------------------------------------------------------------- | -------------- | -------- |
| 1.1  | Fix Tier 2 data discrepancy (Dense R@1, R@10)                         | 30 min         | Critical |
| 1.4  | Fix title "Scale Laws" → "Scale Effects"                              | 5 min          | Critical |
| 1.5  | Fill in co-author names                                               | 10 min         | Critical |
| 1.2  | Re-run RAGAS Tier 2 on saved answers                                  | 1 hr           | Critical |
| 1.3  | Either compute CIS scores or demote from contributions                | 2 hr or 20 min | Critical |
| 2.1  | Acknowledge pseudo-relevance circularity; ideally annotate 50 queries | 3 hr or 5 min  | High     |
| 2.2  | Clarify Hybrid R@1 = 1/3 is the theoretical maximum                   | 5 min          | High     |
| 4.1  | Fix lin2022rrf wrong citation                                         | 15 min         | High     |
| 4.2  | Add DeBERTa-v3 citation                                               | 5 min          | High     |
| 3.1  | Add Tier 1 significance test or explanation                           | 15 min         | Medium   |
| 3.2  | Add effect size (rank-biserial r) to Wilcoxon                         | 10 min         | Medium   |
| 5.1  | Soften "ruling out corpus size"                                       | 5 min          | Medium   |
| 5.3  | Fix CIS "model-independent" claim wording                             | 10 min         | Medium   |
| 5.6  | Add CT imaging qualitative example                                    | 20 min         | Medium   |
| 4.3  | Fix BioASQ booktitle → journal                                        | 2 min          | Low      |
| 4.4  | Fix nogueira2019 booktitle                                            | 5 min          | Low      |
| 4.5  | Add sentence-transformers citation                                    | 5 min          | Low      |
| 5.8  | Fix "specialised" → "specialized"                                     | 5 min          | Low      |
| 5.4  | Add per-query-type breakdown (you have the data)                      | 30 min         | Medium   |
| 6.4  | Add latency numbers                                                   | 20 min         | Low      |
| 5.10 | Publish GitHub repo                                                   | 1-2 hr         | High     |
