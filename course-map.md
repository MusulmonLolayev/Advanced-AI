# Advanced AI - Machine Learning Course Plan

This is the working course plan for the authored material in `ml/` (Module 1), `statistics/`
(Module 0), and `overview/` (a standalone course-intro deck). It reflects the current lecture and
assignment sequence, not the older textbook-first outline.

## Course goal

By the end of this course, students should be able to:

- explain the geometry behind nearest-neighbor methods, PCA, clustering, and density-based outlier screening;
- implement the core computational steps of classical ML algorithms with NumPy;
- interpret when a method is based on distance, projection, density, or optimization;
- compare clustering methods with supervised tree-based methods at a practical level;
- build, train, and evaluate deep neural networks for vision, language, and graph-structured data.

## Course structure

The course is organized into eight modules (0–7). Lecture numbering restarts at 1 within each module.

### Module 0: Statistics for Advanced AI (Lectures 1-10)

Authored under `statistics/` (own `main.tex`, `lectures/`, `theme/`, `scripts/` — mirrors `ml/`'s
layout but is an independent deck, not shared with it). The deck opens with a module
intro (`lecture00_module_intro.tex`), which sits outside the part numbering and is labelled
"Module 0 - Introduction". Within each lecture, part numbering restarts at 0, and each part
divider names its lecture. All ten lectures are drafted, each split
into two part files (e.g. Lecture 1 is Part 0 `lecture01_data_descriptive.tex` and Part 1
`lecture01_probability_basics.tex`); the full deck is 255 frames.

Primary references:
- Illowsky & Dean, *Introductory Statistics 2e* (OpenStax) — Lectures 1–5 core probability and distributions
- Bishop, *PRML* — Lectures 6–7 (MLE, Bayesian inference)
- Cover & Thomas, *Elements of Information Theory* — Lecture 7
- Wainwright & Jordan, *Graphical Models, Exponential Families, and Variational Inference* — Lecture 8
Topics not critical for AI (chi-square tests, two-sample t-tests, ANOVA, study-design methodology)
are omitted. Hypothesis testing is embedded in L10 (model evaluation), its most relevant context.

1. **Lecture 1 - Data, Probability & Descriptive Statistics**
   - data types, frequency distributions, histograms, box plots
   - measures of center and spread (mean, variance, standard deviation, IQR)
   - sample spaces, events, probability rules (complement, addition, multiplication)
   - mutual exclusivity vs. independence; empirical vs. classical probability
2. **Lecture 2 - Conditional Probability, Independence & Bayes' Theorem**
   - conditional probability and the multiplication rule
   - statistical independence, tree diagrams, contingency tables
   - Bayes' theorem: the formula that drives probabilistic ML from Naive Bayes to diffusion models
3. **Lecture 3 - Discrete Random Variables & Key Distributions**
   - probability mass function, expectation, variance
   - Bernoulli and Binomial (binary outputs); Categorical and Multinomial (multi-class outputs, softmax)
   - Poisson (count data, event modeling); Dirichlet as a prior over Categorical (LDA, topic models)
4. **Lecture 4 - Continuous Random Variables & the Gaussian**
   - probability density function, CDF, area-as-probability
   - uniform, exponential (generative sampling), Beta (conjugate prior for Bernoulli/Binomial)
   - the Gaussian: 1D standard normal, z-scores, 68-95-99.7 rule
   - multivariate Gaussian: mean vector, covariance matrix, contour ellipses
   - why the Gaussian appears everywhere: GMMs, VAEs, weight initialization, Bayesian priors
5. **Lecture 5 - The Central Limit Theorem & Maximum Likelihood Estimation**
   - sampling distribution of the mean, standard error, law of large numbers
   - CLT statement and conditions; why mini-batch gradients and batch normalization rely on this
   - likelihood function, log-likelihood; MLE derivations for Gaussian and Bernoulli
   - MLE as the statistical foundation of cross-entropy loss and MSE; bridge to gradient descent
6. **Lecture 6 - Bayesian Inference & MAP Estimation**
   - prior, likelihood, posterior; Bayes' rule as an update rule
   - MAP estimation as regularized MLE (L2 regularization = Gaussian prior)
   - conjugate priors: Beta–Bernoulli, Dirichlet–Categorical, Gaussian–Gaussian
   - Bayesian vs. frequentist framing; predictive distributions
7. **Lecture 7 - Information Theory: Entropy, KL Divergence & Mutual Information**
   - Shannon entropy: measuring uncertainty in a distribution
   - cross-entropy as a loss function; KL divergence as a distance between distributions
   - mutual information: feature selection, VAE objectives, representation learning
8. **Lecture 8 - The Exponential Family & Sufficient Statistics**
   - exponential family form: $p(x|\eta) = h(x)\exp(\eta^\top T(x) - A(\eta))$
   - natural parameters $\eta$, sufficient statistics $T(x)$, log-partition function $A(\eta)$
   - membership: Gaussian, Bernoulli, Categorical, Poisson, Beta, Dirichlet — unified in one family
   - moment identities ($\nabla_\eta A = \mathbb{E}[T(x)]$), Fisher-Neyman factorization theorem
   - connection to GLMs, log-linear models, and variational inference (ELBO with exponential-family posteriors)
9. **Lecture 9 - Correlation, Regression & Multivariate Statistics**
   - Pearson correlation, covariance, scatter plots; ordinary least squares, residuals, R²
   - MLE interpretation of OLS; bridge to regularized regression in Module 1
   - sample covariance matrix, correlation matrix
   - eigendecomposition of the covariance matrix; variance along principal directions
   - statistical preview of PCA before its geometric treatment in Module 1
10. **Lecture 10 - Statistical Model Evaluation**
    - train / validation / test splits; the bias-variance tradeoff as a statistical phenomenon
    - cross-validation, bootstrap confidence intervals on metrics
    - null/alternative hypotheses, p-values, Type I and Type II errors; A/B testing for model comparisons
    - calibration (reliability diagrams), permutation tests for statistical significance

### Module 1: Classical Machine Learning (Lectures 1-14)

Authored under `ml/`. Lectures 1-10 are drafted (`ml/lectures/`), each with a matching lab
(`ml/assignments/assignment1_knn/` through `assignment7_forest_variants/` cover Lectures 1-7;
Lectures 8-10 have no lab yet). Lectures 11-14 below are outline only so far.

1. **Lecture 1 - Introduction to Machine Learning and k-NN**
   - classification, regression, retrieval, anomaly scoring
   - distance, scaling, and the nearest-neighbor rule
2. **Lecture 2 - PCA**
   - linear projection, variance maximization, reconstruction
   - dimensionality reduction and visualization
3. **Lecture 3 - k-Means Clustering**
   - clustering objective, alternating minimization, centroid updates
   - scaling, initialization, and failure modes
4. **Lecture 4 - DBSCAN**
   - epsilon neighborhoods, MinPts, core/border/noise points
   - density reachability, density connectivity, outlier screening
5. **Lecture 5 - Decision Trees**
   - impurity measures: Gini index and information gain (entropy and mutual information applied — Module 0 L7)
   - recursive splitting, tree growth, pruning, interpretability
6. **Lecture 6 - Random Forests**
   - bagging, feature subsampling, variance reduction
7. **Lecture 7 - Forest Variants: Isolation Forest, Extra-Trees, Quantile Forests**
   - Isolation Forest: anomaly scoring via random partitioning depth
   - Extremely Randomized Trees (Extra-Trees): random split thresholds, variance reduction
   - Quantile Regression Forests: predictive intervals from forest leaves
8. **Lecture 8 - Boosting**
   - weak learners, additive modeling, sequential correction
9. **Lecture 9 - Gaussian Mixture Models & EM**
   - soft/probabilistic clustering, latent variables
   - the EM algorithm
10. **Lecture 10 - High-Dimensional Visualization**
    - `t-SNE` as a visualization tool
    - contrast with PCA and cluster inspection
11. **Lecture 11 - Practical Gradient Boosting**
    - XGBoost, LightGBM, CatBoost
    - applied tuning of boosted trees
12. **Lecture 12 - Regularized Regression: Ridge, Lasso & Elastic Net**
    - OLS as the starting point (derivation in Module 0 L9); the problem of overfitting in high dimensions
    - Ridge (L2) and its MAP interpretation (Gaussian prior from Module 0 L6); Lasso (L1) and sparsity
    - Elastic Net; gradient-descent fitting of regularized objectives; the regularization path
13. **Lecture 13 - Logistic Regression & Linear Classifiers**
    - logistic regression: sigmoid, cross-entropy loss as MLE (Module 0 L5 and L7)
    - SVM margins, softmax for multi-class
    - bridges into the loss-function view used in Module 2
14. **Lecture 14 - Classification Metrics, ROC/AUC & Hyperparameter Optimization**
    - precision, recall, F1; confusion matrix; ROC curve and AUC
    - bias-variance tradeoff recap (Module 0 L10); model selection with cross-validation (Module 0 L10)
    - Bayesian hyperparameter optimization: Gaussian Processes as surrogate models, acquisition functions

### Module 2: Vision / Deep Neural Networks (Lectures 1-18)

This module follows the Stanford CS231n lecture sequence directly (already translated and
recorded as a separate video series). Some early overlap with Module 1 (e.g. k-NN, linear
classifiers, loss functions) is intentional, not a gap -- it reflects CS231n's own structure
and that material is treated as already covered.

1. **Lecture 1 - Introduction**
   - computer vision overview, course overview
2. **Lecture 2 - Image Classification with Linear Classifiers**
   - the data-driven approach, k-NN, linear classifiers, softmax loss
3. **Lecture 3 - Regularization and Optimization**
   - SGD, momentum, AdaGrad, Adam, learning rate schedules
4. **Lecture 4 - Neural Networks and Backpropagation**
   - multi-layer perceptrons, backpropagation
5. **Lecture 5 - Image Classification with CNNs**
   - convolution and pooling, higher-level representations
6. **Lecture 6 - CNN Architectures**
   - batch normalization, transfer learning, AlexNet, VGG, ResNet
7. **Lecture 7 - Recurrent Neural Networks**
   - RNN, LSTM, GRU, language modeling, image captioning, seq2seq
8. **Lecture 8 - Attention and Transformers**
   - self-attention, Transformers, Vision Transformers (ViT)
9. **Lecture 9 - Object Detection, Image Segmentation, Visualizing and Understanding**
   - single/two-stage detectors, semantic/instance/panoptic segmentation
   - feature visualization, adversarial examples, DeepDream, style transfer
10. **Lecture 10 - Video Understanding**
    - video classification, 3D CNNs, two-stream networks, multimodal video
11. **Lecture 11 - Large Scale Distributed Training**
    - parallelism, activation checkpointing
12. **Lecture 12 - Self-Supervised Learning**
    - pretext tasks, contrastive learning, multisensory supervision
13. **Lecture 13 - Generative Models 1**
    - variational autoencoders, GANs, autoregressive models
14. **Lecture 14 - Generative Models 2**
    - diffusion models
15. **Lecture 15 - 3D Vision**
    - 3D shape representations, shape reconstruction, neural implicit representations
16. **Lecture 16 - Vision and Language**
17. **Lecture 17 - World Modeling**
18. **Lecture 18 - Human-Centered AI**

### Module 3: Natural Language Processing (Lectures 1-15)

Classical NLP first, then deep/neural NLP -- mirrors the same classical-to-deep arc used by
Modules 1 and 2.

1. **Lecture 1 - Text Preprocessing & Representation**
   - tokenization, stemming/lemmatization, Bag-of-Words, TF-IDF
2. **Lecture 2 - Classical Language Models**
   - N-grams, smoothing
3. **Lecture 3 - Sequence Labeling: POS Tagging with HMMs**
   - Hidden Markov Models, Viterbi decoding
4. **Lecture 4 - Syntactic Parsing**
   - constituency and dependency parsing, context-free grammars
5. **Lecture 5 - Information Retrieval & Topic Modeling**
   - vector space model, cosine similarity, LDA/LSA
6. **Lecture 6 - Classical Text Classification**
   - Naive Bayes / SVM on TF-IDF features, sentiment analysis
7. **Lecture 7 - Word Embeddings**
   - Word2Vec, GloVe, distributional semantics
8. **Lecture 8 - Neural Language Models**
   - RNN/LSTM/GRU architecture assumed known (Module 2 L7); focus is the language modeling objective
   - next-token prediction, perplexity as exponentiated cross-entropy (Module 0 L7)
   - teacher forcing, exposure bias, scheduled sampling
9. **Lecture 9 - Sequence-to-Sequence & Neural Machine Translation**
10. **Lecture 10 - Attention for NLP**
    - Transformer architecture assumed known (Module 2 L8); NLP-specific adaptations
    - positional encodings for variable-length text; additive vs. multiplicative attention variants
    - masking strategies: padding masks, causal masks for autoregressive decoding
11. **Lecture 11 - Pretrained Transformers: Objectives & Architectures**
    - encoder-only (BERT): masked-LM and next-sentence prediction objectives
    - decoder-only (GPT): autoregressive LM; encoder-decoder (T5, BART): span corruption
    - tokenization: BPE, WordPiece, SentencePiece; subword vocabulary trade-offs
12. **Lecture 12 - Fine-tuning & Adapting Pretrained Models**
    - full fine-tuning vs. feature extraction; catastrophic forgetting
    - task-specific heads: classification, span extraction (QA), generation
    - named entity recognition and extractive question answering as worked examples
13. **Lecture 13 - Scaling Laws & Large Language Models**
    - Chinchilla scaling laws: compute-optimal training
    - emergent abilities, in-context learning, chain-of-thought prompting
    - instruction tuning (FLAN, InstructGPT); RLHF overview (mathematical foundations in Module 5)
14. **Lecture 14 - Retrieval-Augmented Generation & Evaluation**
    - RAG pipeline overview (dense retrieval architecture detail in Module 7)
    - embedding-based retrieval, chunking strategies, context-window limits
    - LLM evaluation: BLEU/ROUGE, human preference, HELM, Chatbot Arena
15. **Lecture 15 - Multimodal Language Models**
    - vision-language pretraining: CLIP (contrastive), Flamingo, LLaVA
    - image captioning, visual question answering, text-to-image generation
    - grounding language in perception: challenges and current frontiers

### Module 4: Graph Neural Networks (Lectures 1-5)

1. **Lecture 1 - Why Graph Neural Networks? Classic Tasks**
   - node classification, link prediction, graph classification
   - why standard NNs fail on graph-structured data
2. **Lecture 2 - Graph Theory & Representation Basics**
   - nodes, edges, adjacency matrices, graph types
3. **Lecture 3 - Message Passing & Graph Convolutions**
   - spectral vs. spatial methods, GCN
4. **Lecture 4 - Modern GNN Architectures**
   - GraphSAGE, Graph Attention Networks, GIN
5. **Lecture 5 - GNN Applications in Practice**
   - recommendation systems (e.g. PinSAGE), molecule property prediction, fraud detection

### Module 5: Reinforcement Learning & Alignment (being authored separately)

MDPs, value functions, policy gradients, PPO, RLHF, DPO. Foundational mathematics treated
here, not scattered across Modules 1–3. Forward-referenced in Module 1 L14 (Gaussian Processes
/ Bayesian optimization) and Module 3 L13 (RLHF overview).

### Module 6: Efficient AI & Deployment (Lectures 1-8)

1. **Lecture 1 - Model Compression: Pruning & Quantization**
   - structured vs. unstructured pruning; magnitude and gradient-based criteria
   - post-training quantization (PTQ): INT8, INT4, GPTQ; quantization-aware training (QAT)
   - trade-offs: accuracy, memory footprint, inference latency
2. **Lecture 2 - Knowledge Distillation**
   - teacher–student framework; soft targets and temperature scaling
   - feature-level distillation (intermediate representations); self-distillation
   - application to LLM compression (DistilBERT, Alpaca-style distillation)
3. **Lecture 3 - Parameter-Efficient Fine-Tuning: LoRA & QLoRA**
   - motivation: full fine-tuning cost at LLM scale
   - low-rank adaptation (LoRA): decomposition, rank selection, merging at inference
   - QLoRA: 4-bit base model + LoRA adapters; practical memory budgets
   - adapter methods, prefix tuning, and prompt tuning as alternatives
4. **Lecture 4 - Inference Optimization: KV Cache, Speculative Decoding & Continuous Batching**
   - autoregressive decoding bottleneck; key-value cache mechanics
   - speculative decoding: draft model + verifier; acceptance rate analysis
   - continuous batching vs. static batching; PagedAttention (vLLM)
   - FlashAttention: IO-aware exact attention; memory and speed gains
5. **Lecture 5 - Serving Infrastructure: vLLM, TensorRT & ONNX**
   - model serving architecture: load balancing, replicas, routing
   - vLLM: paged KV cache, throughput benchmarks
   - TensorRT and ONNX: graph optimization, kernel fusion, deployment pipelines
   - multi-GPU serving: tensor parallelism, pipeline parallelism at inference time
6. **Lecture 6 - Evaluation & Benchmarking at Scale**
   - latency vs. throughput trade-offs; time-to-first-token, tokens-per-second
   - hardware utilization: MFU (model FLOP utilization), memory bandwidth bounds
   - standard benchmarks: MLPerf, LM-Eval Harness; cost-per-token analysis
7. **Lecture 7 - Edge Deployment: Mobile, WASM & Embedded**
   - on-device inference constraints: memory, power, latency SLAs
   - CoreML, ONNX Runtime Mobile, TFLite; WebAssembly for browser inference
   - LLM on-device: llama.cpp, MLC-LLM; model selection for edge targets
8. **Lecture 8 - Responsible Deployment: Monitoring, Drift & Safety Guardrails**
   - production monitoring: latency/error dashboards, output logging
   - distribution shift and concept drift detection; model refresh strategies
   - safety guardrails: input/output filtering, constitutional AI, red-teaming
   - deployment checklists: bias auditing, rate limiting, fallback policies

### Module 7: AI Agents, Tool Use & Retrieval (Lectures 1-8)

Authored under `agents/` (own `main.tex`, `lectures/`, `theme/`, `scripts/`). All eight lectures
are drafted: the deck opens with a module intro outside the part numbering, then Lecture 1 as a
single part and Lectures 2-8 each split into two part files, 209 frames in total. Lectures are
jurisdiction-neutral — they teach algorithms and cite papers — while one Uzbek Labor Code article
runs through the whole module as the worked example (chunked in L5, embedded in L6, indexed in L7,
attacked in L8), and the capstone below is where jurisdiction-specific work lives.

**The class agent** (`agents/class_agent/`) is built together in class, one step per lecture, on the real Labor Code
(581 articles from the capstone corpus, pinned). Each step has recorded runs that replay offline and a session plan in
`sessions/`. Lecture 1 (the ReAct loop) is done; its runs replaced the slide's invented worked trace: the real code
answers the under-18 half (Art. 415: 36 h at 16-18, 24 h at 15-16), so it is not an abstention example.

1. **Lecture 1 - What is an Agent? ReAct, Tool Use & Action Loops**
   - agents vs. pipelines: when a model controls its own next step
   - ReAct: interleaving reasoning traces and actions; scratchpad pattern
   - tool use primitives: search, code execution, API calls; action space design
   - failure modes: infinite loops, hallucinated tool calls, compounding errors
2. **Lecture 2 - Function Calling & Structured Outputs**
   - function/tool schemas: JSON Schema, OpenAPI; how models learn to call tools
   - structured output generation: constrained decoding, grammar-guided sampling
   - parallel vs. sequential tool calls; tool result injection into context
3. **Lecture 3 - Memory: In-Context, External & Episodic**
   - in-context memory: context window limits, prompt compression, summarization
   - external memory: key-value stores, document stores, episodic buffers
   - retrieval-augmented memory vs. fine-tuned memory; MemGPT architecture
4. **Lecture 4 - Multi-Agent Orchestration**
   - orchestrator–subagent pattern; task decomposition and delegation
   - message-passing protocols: shared memory vs. structured communication
   - frameworks: LangGraph, AutoGen, CrewAI; trust and permission boundaries
   - failure recovery: retry logic, fallback agents, human-in-the-loop checkpoints
5. **Lecture 5 - Retrieval-Augmented Generation: Architecture End-to-End**
   - RAG pipeline: query → retrieve → augment → generate
   - chunking strategies: fixed-size, sentence, semantic, hierarchical
   - reranking: cross-encoder rerankers, reciprocal rank fusion
   - advanced RAG: HyDE, multi-hop retrieval, iterative refinement
6. **Lecture 6 - Dense Retrieval & Embedding Models**
   - bi-encoder architecture; contrastive training (in-batch negatives, hard negatives)
   - embedding model families: E5, BGE, GTE, OpenAI Ada; MTEB benchmark
   - late interaction models: ColBERT; sparse–dense hybrid retrieval (BM25 + dense)
7. **Lecture 7 - Vector Databases & ANN Search**
   - approximate nearest neighbor (ANN) algorithms: HNSW, IVF, PQ, ScaNN
   - vector database landscape: Pinecone, Weaviate, Qdrant, pgvector
   - indexing trade-offs: recall vs. latency vs. memory; metadata filtering
   - scaling: sharding, replication, incremental index updates
8. **Lecture 8 - Agent Evaluation, Safety & Failure Modes**
   - agent evaluation frameworks: trajectory scoring, tool-call accuracy, task completion
   - benchmarks: AgentBench, WebArena, SWE-bench; human vs. automated eval
   - safety: prompt injection attacks, tool misuse, sandboxing code execution
   - alignment in agentic systems: minimal footprint, reversibility, human oversight

#### Module 7 capstone project: a grounded legal research agent

Module 7 is assessed by one team project rather than a lab sequence. It is scoped as a
**legal research agent that must ground every claim in a retrieved article, plus a harness that
measures when it fails** — deliberately *not* "an agent that answers legal questions". The
reframing matters for three reasons: retrieval can be scored against article IDs instead of
judged by eye; the failure mode is the lecture material rather than an accident; and confining
the agent to "find and cite passages in this corpus" keeps it clear of unauthorized-practice
questions that advice-giving would raise.

**Corpus.** Uzbek national legislation, article-structured, from lex.uz:

- `javohirmat/uzbek-legal-corpus` (GitHub) — Constitution + 20 codes + 4 laws, 7,368 articles,
  ~971k words, article-level JSONL (`code`, `article_id`, `section`, `chapter`, `text`,
  `lex_uz_doc`, `snapshot_date`). Data CC0, code MIT. Good default: small, audited, stable.
- `sukhrobnurali/uzbek-legal-corpus` (Hugging Face) — 24,267 acts / 54,173 article rows,
  1991-2026, adding `amendment_note`, `version_date`, `cross_references`, `okoz_codes`,
  `quality_flag`. Use when a team needs temporal or multi-hop ground truth.

Legislative text is not copyrightable under Art. 8 of the Law on Copyright and Related Rights.

**Lectures stay jurisdiction-neutral.** The slides teach algorithms and papers; Uzbek law appears
only as the running worked example (one Labor Code article carried through all eight lectures —
chunked in L5, embedded in L6, indexed in L7, attacked in L8) and as the project corpus. Same
device as the bike/bus year group in Module 0 Lecture 2.

**Ground truth without annotators.** The corpus metadata supplies most of the labels:

1. *Query-from-article inversion* — pick an article, write a question it answers; that article ID
   is the gold span. This is how LegalBench-RAG was built (generative queries traced back to
   corpus locations), so the method is citable rather than improvised.
2. *`cross_references`* — article A cites article B, giving free two-hop retrieval items with a
   known answer set. Benchmarks the multi-hop material in L5.
3. *`amendment_note` + `version_date`* — "what did Article X say before date D" tests corpus
   versioning, a failure mode real legal tools have.
4. *Deleted-span holdout* — remove the supporting article for a subset of queries; a correct agent
   must abstain. Needs no labels, and measures groundedness directly.
5. *Student annotation with inter-annotator agreement* — where teams do label, require Cohen's
   kappa, which cashes out Module 0's statistics.

**Sprints** (following the Stanford CS224G cadence — four two-week sprints, checkpoint-weighted):

1. After L1-L2 — ReAct loop, tool schemas, structured cited output. Naive chunking baseline plus a
   20-query smoke eval.
2. After L5-L7 — the retrieval stack: chunking strategy, embeddings, ANN index, hybrid BM25+dense,
   reranking. Scored as recall@k against the sprint-1 baseline.
3. After L3-L4 — multi-turn memory, and a verifier subagent that checks each claim against its
   cited article. Orchestrator/subagent pattern.
4. After L8 — evaluation harness, abstention behaviour, red team (a planted article containing
   "ignore previous instructions").

**Deliverables:** repo; 2-minute demo video; 4-page technical report whose centrepiece is the
eval table, not the demo; red-team appendix. Grade the harness as heavily as the agent — every
team's demo looks convincing, which is exactly what Magesh et al. (2024) demonstrated empirically.

**Two traps that are lessons, not accidents.** The corpus uses U+02BB and U+02BC for the okina in
*oʻ/gʻ* and the tutuq belgisi, never ASCII apostrophes. Unicode normalization is *not* the problem —
both are category Lm (modifier letters) and NFC/NFD/NFKC/NFKD all leave them unchanged. The problem
is tokenization: `\w+` keeps U+02BB inside the word, giving one token `oʻrtacha`, but splits on the
ASCII apostrophe, giving `o` + `rtacha`. So a keyboard-typed query and the corpus produce different
token streams and match nothing, and because the two glyphs look nearly identical the failure is
silent. The bug is normalizing corpus and query *differently* — the concrete answer to "why did
retrieval fail" in L6. And only about half
of lex.uz acts have a Latin-script version, the rest being Russian or Cyrillic, which forces the
cross-lingual retrieval discussion honestly. No Uzbek-specific retrieval evaluation exists in the
literature, so a team that produces one has done something new; it also justifies treating BM25 as
a strong baseline, since legal Uzbek is formulaic.

#### Module 7 model and cost baseline

The project runs against a **cheap hosted API**, not a locally served model — a 7B-class model at
usable speed needs a GPU most students do not have, and that is a hard blocker rather than a
teaching opportunity. Pin one model in the handout so eval numbers are comparable across teams.

**Baseline: DeepSeek V4.1-Flash** (prices per 1M tokens, snapshot 2026-09-24 — DeepSeek adjusts
these frequently, so re-check before each cohort):

| | input | cached input | output |
|---|---|---|---|
| off-peak | $0.15 | $0.003 | $0.60 |
| peak | $0.30 | $0.006 | $1.20 |

**Schedule labs after 15:00 Tashkent time.** Peak is 01:00-04:00 and 06:00-10:00 UTC on weekdays,
which is 06:00-09:00 and 11:00-15:00 local (UTC+5). An early-afternoon lab pays double for exactly
the same work.

**Budget.** A 500-query eval run driving ~3 tool calls per query (~6k input, ~600 output tokens
per query) costs about $0.63 off-peak, or **~$0.25 with prefix caching** — the system prompt and
few-shot block repeat on every query and DeepSeek caches prefixes automatically. Forty full eval
runs plus development traffic comes to roughly **$25-50 per team**, so **$250-500 for a class of
ten teams**. A departmental line item, not a barrier.

**Free tiers do not work here.** Provider free quotas run to a few hundred to a thousand requests
per day; one 500-query eval run at 3 tool calls is 1,500 requests. Relying on a free tier just
teaches students to shrink their eval set, which defeats the design.

**Embeddings are a separate decision from generation.** BGE-M3 over the 7,368-article corpus is a
one-time CPU encode of ~1.4M tokens — about an hour on a laptop, no GPU, free afterwards and
offline. A hosted embedding API costs cents for the same corpus. Decide deliberately rather than
by default.

**Before the syllabus commits:** verify multi-step tool-calling and strict-JSON-schema behaviour
on the pinned model against the actual corpus (Lectures 1-2 depend on it), and confirm that a
workable payment method is available locally.

#### Module 7 reading list (per lecture)

1. **Agents & action loops** — ReAct (Yao et al., 2023); Reflexion (Shinn et al., 2023);
   Toolformer (Schick et al., 2023).
2. **Function calling & structured outputs** — Gorilla (Patil et al., 2023); grammar-constrained
   decoding (Willard & Louf, 2023); JSON Schema / OpenAPI tool specs.
3. **Memory** — MemGPT (Packer et al., 2023); Lost in the Middle (Liu et al., 2023).
4. **Multi-agent orchestration** — AutoGen (Wu et al., 2023); Generative Agents (Park et al.,
   2023); LangGraph documentation on orchestrator-subagent graphs; *At Equal Inference Cost,
   Multi-Agent Structure Does Not Beat a Single Frozen Agent* (Dylan et al., 2026,
   arXiv:2609.04217) — the fixed-model-call comparison that most multi-agent papers skip.
5. **RAG end-to-end** — RAG (Lewis et al., 2020); Fusion-in-Decoder (Izacard & Grave, 2021);
   HyDE (Gao et al., 2022); Self-RAG (Asai et al., 2023); cross-encoder reranking (Nogueira & Cho,
   2019); reciprocal rank fusion (Cormack, Clarke & Buettcher, 2009).
6. **Dense retrieval & embeddings** — DPR (Karpukhin et al., 2020); ColBERT (Khattab & Zaharia,
   2020); BGE-M3 (Chen et al., 2024); MTEB (Muennighoff et al., 2022); BM25 (Robertson &
   Zaragoza, 2009) as the baseline that must be beaten.
7. **Vector databases & ANN search** — HNSW (Malkov & Yashunin, 2018); product quantization
   (Jegou, Douze & Schmid, 2011); ScaNN (Guo et al., 2020); FAISS (Johnson et al., 2019).
8. **Evaluation, safety & failure modes** — LegalBench (Guha et al., 2023); LegalBench-RAG
   (ZeroEntropy, 2024); *Hallucination-Free? Assessing the Reliability of Leading AI Legal
   Research Tools* (Magesh, Surani, Dahl, Suzgun, Manning & Ho, 2024 — 17-33% hallucination in
   tools marketed as eliminating it, and the best single teaching artifact in the module);
   indirect prompt injection (Greshake et al., 2023); AgentBench (Liu et al., 2023);
   WebArena (Zhou et al., 2023); SWE-bench (Jimenez et al., 2023); RAGAS (Es et al., 2023).

Open decisions: whether teams may substitute an English contract corpus (CUAD / ContractNLI via
LegalBench-RAG) to get annotated spans at the cost of local relevance; and team size, currently
assumed 2-4 following CS224G's 2-5.

## Topics intentionally excluded

- **Hierarchical clustering** -- lower priority than GMM; k-means + DBSCAN + GMM already
  cover the three major clustering paradigms (partition, density, probabilistic).
- Most of Bishop's *Pattern Recognition and Machine Learning* (graphical models, MCMC/Gibbs
  sampling, Probabilistic PCA, Relevance Vector Machines, Bayesian model averaging) --
  theoretical/Bayesian territory largely superseded in modern practice. Exceptions retained:
  variational inference (Module 2, Lecture 13), Gaussian Processes as a surrogate model
  (Module 1, Lecture 14), Bayesian inference foundations (Module 0, Lecture 6).

## Assignment sequence

1. **Lab 1 - k-NN**
2. **Lab 2 - PCA**
3. **Lab 3 - k-Means**
4. **Lab 4 - DBSCAN**
5. **Lab 5 - Decision Trees**
6. **Lab 6 - Random Forests**
7. **Lab 7 - Forest Variants (Isolation Forest)**

Assignments currently only cover Module 1; later modules may get their own lab sequence as
they are authored. Module 7 is the exception by design: it is assessed by a single team capstone
(see the Module 7 section above) rather than a lab sequence.

## Notes

- Keep the notation consistent across lectures and assignments.
- Prefer short derivations followed by numerical examples and graphics.
- Use the course split to introduce supervised tree methods before the NN block.
- Module 2 (Vision/CS231n) already exists as a separate translated video series; authoring
  `.tex` lecture decks for it in this repo is a separate, later task.
