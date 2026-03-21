#!/bin/bash

# Shared script constants for Assignment 1 data preparation tooling.
ENV_NAME="advanced-ai-assignment1-knn-data"

CORE_REQUIREMENTS=(
  "numpy>=1.24"
  "requests>=2.31"
  "scikit-learn>=1.3"
)

RETRIEVAL_REQUIREMENTS=(
  "sentence-transformers>=2.6"
  "beir>=2.0"
  "tqdm>=4.66"
)
