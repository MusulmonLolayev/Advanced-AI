#!/bin/bash

ZIP_FILENAME="assignment2_pca_submission.zip"

REQUIRED=(
  "advanced_ai/pca.py"
  "advanced_ai/self_checks.py"
  "pca.ipynb"
  "collect_submission.ipynb"
  "pca_text_embeddings.py"
  "pca_anomaly_detection.py"
  "pca_knn_comparison.py"
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
  pca.ipynb \
  collect_submission.ipynb \
  makepdf.py \
  pca_text_embeddings.py \
  pca_anomaly_detection.py \
  pca_knn_comparison.py \
  pca_whitening_optional.py \
  requirements.txt \
  advanced_ai \
  results \
  -x '*/__pycache__/*' '*.pyc' '*/.ipynb_checkpoints/*'

echo "Created ${ZIP_FILENAME}"
