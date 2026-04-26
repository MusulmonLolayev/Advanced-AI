#!/bin/bash

ZIP_FILENAME="assignment3_kmeans_submission.zip"

REQUIRED=(
  "advanced_ai/clustering/kmeans.py"
  "advanced_ai/self_checks.py"
  "kmeans.ipynb"
  "collect_submission.ipynb"
  "iris_clustering.py"
  "initialization_scaling_study.py"
  "pca_projection_clustering.py"
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
  kmeans.ipynb \
  collect_submission.ipynb \
  makepdf.py \
  iris_clustering.py \
  initialization_scaling_study.py \
  pca_projection_clustering.py \
  image_quantization_optional.py \
  requirements.txt \
  advanced_ai \
  results \
  -x '*/__pycache__/*' '*.pyc' '*/.ipynb_checkpoints/*'

echo "Created ${ZIP_FILENAME}"
