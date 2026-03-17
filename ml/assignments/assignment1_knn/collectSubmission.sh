#!/bin/bash
set -euo pipefail

ZIP_FILENAME="assignment1_knn_submission.zip"

REQUIRED=(
  "README.md"
  "advanced_ai/classifiers/k_nearest_neighbor.py"
  "advanced_ai/self_checks.py"
  "knn.ipynb"
  "collect_submission.ipynb"
  "banknote_classification.py"
  "california_regression.py"
)

for FILE in "${REQUIRED[@]}"
do
  if [ ! -f "${FILE}" ]; then
    echo "Required file ${FILE} not found."
    exit 1
  fi
done

rm -f "${ZIP_FILENAME}"
zip -q -r "${ZIP_FILENAME}" \
  README.md \
  banknote_classification.py \
  california_regression.py \
  collect_submission.ipynb \
  knn.ipynb \
  makepdf.py \
  text_retrieval_optional.py \
  network_anomaly_optional.py \
  requirements.txt \
  advanced_ai \
  datasets/README.md \
  results

echo "Created ${ZIP_FILENAME}"
