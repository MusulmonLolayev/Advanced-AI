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

The course is organized into four modules. Lecture numbering restarts at 1 within each module.

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
   - impurity, splits, tree growth, interpretability
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
12. **Lecture 12 - Linear Regression & Regularization**
    - closed-form and gradient-descent fitting
    - Ridge, Lasso, Elastic Net
13. **Lecture 13 - Logistic Regression & Linear Classifiers**
    - logistic regression, SVM margins, softmax
    - bridges into the loss-function view used in Module 2
14. **Lecture 14 - Model Evaluation & Hyperparameter Tuning**
    - bias-variance tradeoff, cross-validation
    - ROC/AUC, Bayesian optimization (ties to Gaussian Processes)

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
   - RNN-based language models, perplexity
9. **Lecture 9 - Sequence-to-Sequence & Neural Machine Translation**
10. **Lecture 10 - Attention Mechanisms in NLP**
    - alignment, additive/multiplicative attention
11. **Lecture 11 - Transformers for NLP**
    - self-attention applied to language, masked-LM objective
12. **Lecture 12 - Pretrained Language Models I: BERT & Masked LM**
13. **Lecture 13 - Pretrained Language Models II: GPT & Autoregressive LM**
14. **Lecture 14 - Named Entity Recognition & Question Answering**
15. **Lecture 15 - Large Language Models in Practice**
    - prompting, instruction tuning, RAG, RLHF

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

## Topics considered and intentionally excluded

- **Reinforcement Learning** -- requires its own mathematical foundation (MDPs, Bellman
  equations, dynamic programming) rather than fitting as a single NN-architecture lecture;
  excluded to keep the course scope disciplined.
- **Hierarchical clustering** -- lower priority than GMM, since k-means + DBSCAN + GMM already
  cover the three major clustering paradigms (partition, density, probabilistic).
- Most of Bishop's *Pattern Recognition and Machine Learning* (graphical models, MCMC/Gibbs
  sampling, Probabilistic PCA, Relevance Vector Machines, Bayesian model averaging, etc.) --
  theoretical/Bayesian-statistics territory, largely superseded in modern practice. Exceptions
  folded into existing lectures: variational inference (Module 2, Lecture 13), Gaussian
  Processes (Module 1, Lecture 14), Mixture-of-Experts (Module 3, Lecture 15).

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
