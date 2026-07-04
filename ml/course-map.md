# Advanced AI - Machine Learning Course Plan

This is the working course plan for the authored material in `ml/`.
It reflects the current lecture and assignment sequence, not the older textbook-first outline.

## Course goal

By the end of this course, students should be able to:

- explain the geometry behind nearest-neighbor methods, PCA, clustering, and density-based outlier screening;
- implement the core computational steps of classical ML algorithms with NumPy;
- interpret when a method is based on distance, projection, density, or optimization;
- compare clustering methods with supervised tree-based methods at a practical level;
- build, train, and evaluate deep neural networks for vision, language, and graph-structured data.

## Course structure

The course is organized into five modules. Lecture numbering restarts at 1 within each module.

### Module 0: Statistics for Advanced AI (Lectures 1-14)

Primary references:
- Illowsky & Dean, *Introductory Statistics 2e* (OpenStax) — Lectures 1–7 core probability and distributions
- Bishop, *PRML* — Lectures 8–9 (MLE, Bayesian inference)
- Cover & Thomas, *Elements of Information Theory* — Lecture 10
- Wainwright & Jordan, *Graphical Models, Exponential Families, and Variational Inference* — Lecture 11
Topics not critical for AI (chi-square tests, two-sample t-tests, ANOVA, study-design methodology)
are deliberately omitted. Hypothesis testing is retained but moved to L14 where it is applied
directly to model evaluation, its most relevant AI context.

1. **Lecture 1 - Data & Descriptive Statistics**
   - data types, frequency distributions, histograms, box plots
   - measures of center (mean, median, mode) and spread (variance, standard deviation, IQR)
   - why understanding feature distributions matters before any ML step
2. **Lecture 2 - Probability Foundations**
   - sample spaces, events, classical and empirical probability
   - complement, addition, and multiplication rules; mutual exclusivity vs. independence
3. **Lecture 3 - Conditional Probability, Independence & Bayes' Theorem**
   - conditional probability and the multiplication rule
   - statistical independence, tree diagrams, contingency tables
   - Bayes' theorem: the formula that drives probabilistic ML from Naive Bayes to diffusion models
4. **Lecture 4 - Discrete Random Variables & Key Distributions**
   - probability mass function, expectation, variance
   - Bernoulli and Binomial (binary outputs); Categorical and Multinomial (multi-class outputs, softmax)
   - Poisson (count data, event modeling); Dirichlet as a prior over Categorical (preview of LDA and topic models)
5. **Lecture 5 - Continuous Random Variables**
   - probability density function, CDF, area-as-probability
   - uniform distribution; exponential distribution (waiting times, generative sampling)
   - Beta distribution: the continuous [0,1]-valued RV and natural conjugate prior for Bernoulli/Binomial
6. **Lecture 6 - The Gaussian Distribution: 1D and Multivariate**
   - standard normal, z-scores, the 68-95-99.7 rule
   - multivariate Gaussian: mean vector, covariance matrix, contour ellipses
   - why the Gaussian appears everywhere: GMMs, VAEs, Bayesian priors, neural network weight init
7. **Lecture 7 - The Central Limit Theorem & Sampling Distributions**
   - sampling distribution of the mean, standard error
   - CLT statement and conditions; law of large numbers
   - why mini-batch gradients and batch normalization rest on these results
8. **Lecture 8 - Maximum Likelihood Estimation**
   - likelihood function, log-likelihood, MLE derivations for Gaussian and Bernoulli
   - MLE as the statistical foundation of cross-entropy loss and MSE loss
   - numerical optimization of the likelihood: the bridge from statistics to gradient descent
9. **Lecture 9 - Bayesian Inference & MAP Estimation**
   - prior, likelihood, posterior; Bayes' rule as an update rule
   - MAP estimation as regularized MLE (L2 regularization = Gaussian prior)
   - conjugate priors (Beta–Bernoulli, Dirichlet–Categorical, Gaussian–Gaussian); Bayesian vs. frequentist framing
10. **Lecture 10 - Information Theory: Entropy, KL Divergence & Mutual Information**
    - Shannon entropy: measuring uncertainty in a distribution
    - cross-entropy as a loss function; KL divergence as a distance between distributions
    - mutual information and its role in feature selection, VAE objectives, and representation learning
11. **Lecture 11 - The Exponential Family & Sufficient Statistics**
    - exponential family form: $p(x|\eta) = h(x)\exp(\eta^\top T(x) - A(\eta))$
    - natural parameters $\eta$, sufficient statistics $T(x)$, log-partition function $A(\eta)$
    - membership: Gaussian, Bernoulli, Categorical, Poisson, Beta, Dirichlet, Gamma — all unified in one family
    - moment identities: $\nabla_\eta A(\eta) = \mathbb{E}[T(x)]$; why this makes MLE and Bayesian updates elegant
    - sufficient statistics and data compression: Fisher-Neyman factorization theorem
    - connection to GLMs, log-linear models, and variational inference (ELBO with exponential-family posteriors)
12. **Lecture 12 - Correlation & Simple Linear Regression**
    - Pearson correlation coefficient, covariance, scatter plots
    - ordinary least squares: derivation, residuals, R²
    - MLE interpretation of OLS; bridge to regularized regression in Module 1
13. **Lecture 13 - Multivariate Statistics: Covariance Matrices & Eigenvectors**
    - sample covariance matrix, correlation matrix
    - eigendecomposition of the covariance matrix; variance along principal directions
    - statistical preview of PCA before its geometric treatment in Module 1
14. **Lecture 14 - Statistical Model Evaluation & Hypothesis Testing**
    - train / validation / test splits; the bias-variance tradeoff as a statistical phenomenon
    - cross-validation, bootstrap confidence intervals on metrics
    - null/alternative hypotheses, p-values, Type I and Type II errors; A/B testing for model comparisons
    - calibration (reliability diagrams), permutation tests for statistical significance

### Module 1: Classical Machine Learning (Lectures 1-14)

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
   - impurity measures: Gini index and information gain (entropy and mutual information applied — Module 0 L10)
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
    - OLS as the starting point (derivation in Module 0 L12); the problem of overfitting in high dimensions
    - Ridge (L2) and its MAP interpretation (Gaussian prior from Module 0 L9); Lasso (L1) and sparsity
    - Elastic Net; gradient-descent fitting of regularized objectives; the regularization path
13. **Lecture 13 - Logistic Regression & Linear Classifiers**
    - logistic regression: sigmoid, cross-entropy loss as MLE (Module 0 L8 and L10)
    - SVM margins, softmax for multi-class
    - bridges into the loss-function view used in Module 2
14. **Lecture 14 - Classification Metrics, ROC/AUC & Hyperparameter Optimization**
    - precision, recall, F1; confusion matrix; ROC curve and AUC
    - bias-variance tradeoff recap (Module 0 L14); model selection with cross-validation (Module 0 L14)
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
   - next-token prediction, perplexity as exponentiated cross-entropy (Module 0 L10)
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

## Topics covered in forthcoming modules

- **Reinforcement Learning & Alignment** (Module 5, being authored separately) -- MDPs, value
  functions, policy gradients, PPO, RLHF, DPO. Foundational mathematics treated there, not
  scattered across Modules 1-3. Forward-referenced in Module 1 L14 (Gaussian Processes / Bayesian
  optimization) and Module 3 L13 (RLHF overview).
- **Efficient AI & Deployment** (Module 6, forthcoming) -- LoRA/QLoRA, quantization, distillation,
  speculative decoding, vLLM, serving infrastructure.
- **AI Agents & Retrieval** (Module 7, forthcoming) -- ReAct, function calling, multi-agent
  orchestration, RAG architecture end-to-end, vector databases, ANN search. Forward-referenced
  in Module 3 L14 (RAG pipeline overview).

## Topics intentionally excluded

- **Hierarchical clustering** -- lower priority than GMM; k-means + DBSCAN + GMM already
  cover the three major clustering paradigms (partition, density, probabilistic).
- Most of Bishop's *Pattern Recognition and Machine Learning* (graphical models, MCMC/Gibbs
  sampling, Probabilistic PCA, Relevance Vector Machines, Bayesian model averaging) --
  theoretical/Bayesian territory largely superseded in modern practice. Exceptions retained:
  variational inference (Module 2, Lecture 13), Gaussian Processes as a surrogate model
  (Module 1, Lecture 14), Bayesian inference foundations (Module 0, Lecture 9).

## Assignment sequence

1. **Lab 1 - k-NN**
2. **Lab 2 - PCA**
3. **Lab 3 - k-Means**
4. **Lab 4 - DBSCAN**
5. **Lab 5 - Decision Trees**
6. **Lab 6 - Random Forests**
7. **Lab 7 - Forest Variants (Isolation Forest)**

Assignments currently only cover Module 1; later modules may get their own lab sequence as
they are authored.

## Notes

- Keep the notation consistent across lectures and assignments.
- Prefer short derivations followed by numerical examples and graphics.
- Use the course split to introduce supervised tree methods before the NN block.
- Module 2 (Vision/CS231n) already exists as a separate translated video series; authoring
  `.tex` lecture decks for it in this repo is a separate, later task.
