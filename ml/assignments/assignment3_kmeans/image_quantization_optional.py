"""Optional image color quantization task for Assignment 3."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.clustering.kmeans import KMeansClustering
from advanced_ai.config import IMAGE_QUANTIZATION_DATA_PATH, RESULTS_DIR, RANDOM_SEED
from advanced_ai.data_utils import load_image_bundle
from advanced_ai.task_utils import require_file


def main() -> None:
    bundle = load_image_bundle(require_file(IMAGE_QUANTIZATION_DATA_PATH))
    image = bundle["image"].astype(np.float64)
    h, w, c = image.shape
    pixels = image.reshape(h * w, c)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for k in [4, 8, 16]:
        model = KMeansClustering(n_clusters=k, max_iter=50, n_init=5, random_state=RANDOM_SEED)
        labels = model.fit_predict(pixels)
        reconstructed = model.cluster_centers_[labels].reshape(h, w, c)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.imshow(np.clip(reconstructed / 255.0, 0.0, 1.0))
        ax.set_title(f"Quantized image with k={k}")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f"image_quantization_k{k}.pdf")
        plt.close(fig)


if __name__ == "__main__":
    main()
