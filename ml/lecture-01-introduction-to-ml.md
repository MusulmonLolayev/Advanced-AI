---
marp: true
theme: default
paginate: true
title: Advanced AI - Lecture 1
description: Introduction to Machine Learning (based on Foundations of Machine Learning, 2nd ed.)
---

# Advanced AI
## Lecture 1: Introduction to Machine Learning

Based on Chapter 1 of *Foundations of Machine Learning* (2nd ed.)  
Mehryar Mohri, Afshin Rostamizadeh, Ameet Talwalkar

---

# Learning goals

By the end of this lecture, you should be able to:

- define machine learning as a formal prediction problem;
- distinguish major ML task types;
- explain train/validation/test roles;
- compare supervised, unsupervised, semi-supervised, online, and RL scenarios;
- describe generalization and the underfitting/overfitting trade-off.

---

# What is machine learning?

Machine learning is the study of algorithms that:

- learn patterns from data;
- improve performance with experience;
- generalize to unseen examples.

Formal view:

- input space: `X`
- output space: `Y`
- hypothesis: `h: X -> Y` (or score space)
- objective: minimize expected loss.

---

# Why machine learning?

Use ML when:

- explicit rules are hard to program;
- data is abundant;
- patterns are complex and high-dimensional;
- decision quality improves with more examples.

Examples: spam filtering, image diagnosis, speech recognition, risk scoring.

---

# Types of ML tasks

- **Classification**: predict category labels (spam/not spam).
- **Regression**: predict real values (house price).
- **Ranking**: order items by relevance.
- **Clustering**: group similar unlabeled points.
- **Dimensionality reduction**: compress data while preserving structure.
- **Structured prediction**: predict sequences/graphs (NLP, bioinformatics).

---

# Running example: spam detection

Goal: classify email as `spam` or `non-spam`.

Pipeline:

- collect labeled emails;
- represent each email with features;
- train classifier;
- tune hyperparameters;
- test on held-out emails.

This example illustrates most concepts in Chapter 1.

---

# Core terminology

- **Example**: one data instance.
- **Feature vector**: numeric representation of an example.
- **Label**: target output.
- **Hypothesis set `H`**: candidate predictors.
- **Loss `L(y, y_hat)`**: penalty for wrong prediction.
- **Hyperparameters**: settings chosen before training.

---

# Learning stages (practical view)

1. Split data.
2. Train on training set.
3. Tune on validation set.
4. Freeze model.
5. Report final performance on test set.

Rule: never tune using test data.

---

# Data split roles

- **Training set**: fit model parameters.
- **Validation set**: model/hyperparameter selection.
- **Test set**: unbiased estimate of final performance.

If data is limited:

- use cross-validation for model selection;
- keep a final untouched test set.

---

# Loss functions

Common losses:

- zero-one loss for classification: `1[y_hat != y]`
- squared loss for regression: `(y_hat - y)^2`
- absolute loss: `|y_hat - y|`
- hinge/logistic losses as convex surrogates

Different losses imply different optimization and behavior.

---

# Risk and empirical risk

- **True risk**: expected loss on the data distribution  
  `R(h) = E[L(y, h(x))]`
- **Empirical risk**: average loss on sample  
  `R_hat(h) = (1/m) * sum_i L(y_i, h(x_i))`

Learning tries to find `h` with low true risk using only sample data.

---

# Learning scenarios

- supervised learning;
- unsupervised learning;
- semi-supervised learning;
- transductive inference;
- online learning;
- reinforcement learning;
- active learning.

Different scenarios change what data is available and when.

---

# Supervised vs unsupervised

**Supervised**

- training data has labels;
- objective is predictive performance on unseen points.

**Unsupervised**

- no labels in training data;
- objective is discover structure (clusters, latent dimensions).

---

# Semi-supervised and transductive

**Semi-supervised**

- small labeled set + large unlabeled set;
- predict future unseen points.

**Transductive**

- labeled training set + fixed unlabeled test points;
- predict only those given test points.

---

# Online learning

Repeated rounds:

1. observe instance;
2. predict;
3. receive true label/loss;
4. update model.

Goal: minimize cumulative loss or regret against best fixed expert in hindsight.

---

# Reinforcement learning

Agent interacts with environment:

- observes state;
- takes action;
- receives reward;
- transitions to new state.

Goal: maximize long-term return, balancing:

- exploration (learn new information);
- exploitation (use known good actions).

---

# Generalization: the central challenge

Machine learning is not memorization.

A model can fit training data perfectly but fail on new data.

Generalization asks:

- why should good training performance imply good test performance?
- when does complexity help vs hurt?

---

# Underfitting vs overfitting

- **Underfitting**: model too simple, high training and test error.
- **Overfitting**: model too complex, low training error but high test error.

Target: choose model complexity that minimizes test/generalization error.

---

# Bias-variance intuition

- high bias: rigid assumptions, misses signal;
- high variance: sensitive to sample noise;
- best models balance both.

Tools to manage trade-off:

- regularization;
- validation/cross-validation;
- more data;
- better features.

---

# Feature engineering matters

From Chapter 1 perspective:

- useful features encode prior knowledge;
- poor features limit even strong algorithms;
- domain expertise and data quality often dominate model choice.

Modern extension: representation learning automates part of feature design.

---

# Typical ML workflow

1. define task and metric;
2. collect and clean data;
3. build features or representations;
4. train baseline models;
5. tune and compare;
6. evaluate robustly;
7. deploy and monitor drift.

---

# Common pitfalls

- data leakage across splits;
- metric mismatch with business/scientific objective;
- class imbalance ignored;
- over-tuning to validation;
- reporting only best-case runs.

Reliable ML requires disciplined evaluation.

---

# From practice to theory

Chapter 1 motivates key theoretical questions:

- how many samples are enough?
- how does hypothesis class size affect learning?
- what guarantees can we prove?

Next lecture: PAC learning framework (Chapter 2).

---

# Quick recap

- ML learns predictors from data to generalize.
- Learning quality depends on data, features, hypothesis class, and loss.
- Train/validation/test separation is essential.
- Generalization drives all design decisions.

---

# In-class check (5 minutes)

1. Why is test data not used for hyperparameter tuning?
2. Give one supervised and one unsupervised problem from your domain.
3. What is one sign of overfitting in an experiment log?

---

# Homework (before Lecture 2)

- Read Chapter 2 sections 2.1-2.4.
- Write a one-page note:
  - define PAC-style guarantee in your own words;
  - explain how sample size should affect confidence.
- Optional coding: implement train/val/test split + baseline classifier.

---

# References

- Mohri, Rostamizadeh, Talwalkar. *Foundations of Machine Learning*, 2nd ed., MIT Press, 2018.
- Course source PDF: `docs/books/ML 1.pdf`

