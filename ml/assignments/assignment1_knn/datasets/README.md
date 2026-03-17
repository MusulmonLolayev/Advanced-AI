# Prepared Data Files

The instructor provides prepared files in this folder so students do not spend time on downloading, cleaning, or feature extraction.

Instructor-side preparation scripts live in `assignment1_knn/scripts/`.

Generated raw caches may be stored under `datasets/_raw/`.

## Required Core Files

### `banknote_authentication.csv`

- comma-separated numeric table
- last column is the binary label
- all previous columns are features

### `california_housing.npz`

Expected keys:

- `X`
- `y`

## Optional Files

### `text_retrieval_embeddings.npz`

Expected keys:

- `query_embeddings`: shape `(num_queries, d)`
- `doc_embeddings`: shape `(num_docs, d)`
- `relevance`: binary matrix of shape `(num_queries, num_docs)`
- `query_lengths`: shape `(num_queries,)`
- `doc_lengths`: shape `(num_docs,)`

Additional metadata may also be present, such as:

- `query_ids`
- `doc_ids`
- `model_name`
- `dataset_name`

### `network_anomaly.npz`

Expected keys:

- `X_train`: normal training examples only
- `X_val`: validation examples
- `y_val`: binary validation labels
- `X_test`: test examples
- `y_test`: binary test labels

These arrays are already numerically encoded and ready for the optional anomaly-detection task.
