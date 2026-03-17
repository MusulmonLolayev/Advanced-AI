# Advanced AI - Assignment 1

This starter provides:

- student-facing task scripts live at the top level of the assignment;
- reusable code lives inside one internal Python package;
- only a small number of functions contain `TODO` blocks;
- self-check scripts verify correctness before students run the real tasks;
- data downloading and repeated experiment code are not part of the student workload.

## Goal

Students should focus on:

- distance computation;
- nearest-neighbor search;
- voting / averaging;
- choosing `k` and a metric on validation data;
- understanding how k-NN behaves in classification, regression, retrieval, and anomaly detection.

Students should **not** spend time on:

- writing data loaders from scratch;
- writing full experiment orchestration loops from scratch;
- writing metric code from scratch;
- building project structure or submission packaging.

## What Students Edit

Required edit zone:

- `advanced_ai/classifiers/k_nearest_neighbor.py`

Everything else is starter infrastructure.

## Assignment Structure

```text
assignment1_knn/
  README.md
  banknote_classification.py
  california_regression.py
  collect_submission.ipynb
  collectSubmission.sh
  environment-data.yml
  knn.ipynb
  makepdf.py
  network_anomaly_optional.py
  requirements.txt
  text_retrieval_optional.py
  advanced_ai/
    config.py
    classifiers/
      k_nearest_neighbor.py
    data_utils.py
    metrics.py
    self_checks.py
    solver.py
    task_utils.py
  datasets/
    README.md
  results/
    keep.md
  scripts/
    check_prepare_all_data.sh
    check_prepare_datasets.sh
    check_prepare_embeddings.sh
    prepare_all_data.py
    prepare_all_data.sh
    prepare_core_datasets.py
    prepare_network_anomaly.py
    prepare_text_retrieval_embeddings.py
```

## Student Workflow

1. Open and follow `knn.ipynb`.
2. Implement all `TODO` blocks in `advanced_ai/classifiers/k_nearest_neighbor.py`.
3. Run:

```bash
python -m advanced_ai.self_checks
```

4. After the self-checks pass, run the real tasks:

```bash
python banknote_classification.py
python california_regression.py
```

5. If you finish early, run at most one optional extension:

```bash
python text_retrieval_optional.py
python network_anomaly_optional.py
```

## Provided Data Convention

The instructor places prepared files inside `datasets/`.

Expected filenames:

- `datasets/banknote_authentication.csv`
- `datasets/california_housing.npz`
- `datasets/text_retrieval_embeddings.npz`
- `datasets/network_anomaly.npz`

See `datasets/README.md` for the expected keys and shapes.

## Instructor Data Prep

If you need to create all prepared artifacts from scratch, run one command from `assignment1_knn/`:

```bash
bash scripts/prepare_all_data.sh
```

The shell wrapper creates and uses a dedicated conda environment named `advanced-ai-assignment1-knn-data`, installs dependencies from the single `requirements.txt`, and then runs all download and preprocessing steps through `conda run`. Core-only runs install only the core section of that file; retrieval-enabled runs also install the retrieval section. When retrieval is enabled, the wrapper bootstraps a CPU PyTorch build before installing the embedding libraries.

Useful variants:

```bash
bash scripts/prepare_all_data.sh --core-only
bash scripts/prepare_all_data.sh --skip-retrieval
bash scripts/prepare_all_data.sh --overwrite
bash scripts/prepare_all_data.sh --skip-install
```

The retrieval pipeline downloads the SciFact BEIR dataset and creates dense embeddings with `sentence-transformers/all-MiniLM-L6-v2`.
The anomaly pipeline downloads KDD Cup 99 via scikit-learn, encodes categorical features, scales numeric features, and writes the final `.npz` bundle expected by the assignment.

If you already have the dependencies installed in the dedicated conda environment, `--skip-install` bypasses the `pip install` step.

For explicit verification after preparation, use:

```bash
bash scripts/check_prepare_datasets.sh
bash scripts/check_prepare_embeddings.sh
bash scripts/check_prepare_all_data.sh
```

The check scripts intentionally reject incompatible preparation flags such as `--core-only`, `--skip-retrieval`, and `--skip-anomaly` when those flags would make a "success" message misleading.

### Retrieval Embeddings

The retrieval preparation script:

- downloads the SciFact split from BEIR;
- builds each document string as `title + " " + text`;
- uses each query string as provided by the dataset;
- encodes both with `sentence-transformers/all-MiniLM-L6-v2`;
- writes L2-normalized dense vectors to `datasets/text_retrieval_embeddings.npz`.

Because the stored vectors are normalized, the optional retrieval task uses cosine distance directly on those embeddings.

## Self-Checks

The self-check script prints text-based correctness checks instead of using a grader.
Typical checks include:

- exact distance matrix comparisons on toy data;
- agreement across `two_loops`, `one_loop`, and `no_loops`;
- expected predictions on toy classification and regression examples;
- anomaly-score sanity checks.

If the script reports failures, students should fix the algorithm before running real tasks.

## Real-Task Expectations

### Required

- `banknote_classification.py`
  - prints validation sweep over `k`, metric, and weighting
  - prints final test accuracy, precision, recall, F1, and confusion matrix

- `california_regression.py`
  - prints validation sweep over `k`, metric, and weighting
  - prints final test MAE and RMSE

### Optional

- `text_retrieval_optional.py`
  - uses instructor-provided query/document embeddings and text lengths
  - prints Recall@5, Recall@10, MRR, and a simple text-length analysis

- `network_anomaly_optional.py`
  - uses distance to the `k`-th nearest neighbor as anomaly score
  - prints ROC-AUC, PR-AUC, and a validation-selected threshold

## Submission

Open `collect_submission.ipynb` or run:

```bash
bash collectSubmission.sh
```

This creates a zip with the code and task scripts. There is no grader in this starter; self-checks and reported metrics are the student's validation mechanism.
