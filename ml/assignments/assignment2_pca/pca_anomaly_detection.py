"""Run the PCA-based anomaly detection task."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from advanced_ai.config import ANOMALY_DATA_PATH, RESULTS_DIR, N_COMPONENT_CHOICES
from advanced_ai.data_utils import load_anomaly_bundle
from advanced_ai.metrics import best_f1_threshold, pr_auc_score_binary, precision_recall_f1, roc_auc_score_binary
from advanced_ai.pca import PrincipalComponentAnalysis
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_anomaly_bundle(require_file(ANOMALY_DATA_PATH))
    X_train = bundle["X_train"]
    X_val = bundle["X_val"]
    y_val = bundle["y_val"].astype(int)
    X_test = bundle["X_test"]
    y_test = bundle["y_test"].astype(int)

    pca = PrincipalComponentAnalysis()
    pca.fit(X_train, method="svd")

    print_section("Validation sweep")
    sweep_rows = []
    for n_components in N_COMPONENT_CHOICES:
        val_scores = pca.reconstruction_error(X_val, n_components=n_components)
        threshold, val_f1 = best_f1_threshold(y_val, val_scores)
        sweep_rows.append((n_components, threshold, val_f1, roc_auc_score_binary(y_val, val_scores)))
        print(
            f"n_components={n_components:>2d} threshold={threshold:.6f} "
            f"val_f1={val_f1:.4f} val_roc_auc={sweep_rows[-1][3]:.4f}"
        )

    best_n_components, best_threshold, _, _ = max(sweep_rows, key=lambda row: row[2])
    test_scores = pca.reconstruction_error(X_test, n_components=best_n_components)
    y_pred = (test_scores >= best_threshold).astype(int)
    prf = precision_recall_f1(y_test, y_pred)

    print_section("Best validation config")
    print(f"n_components = {best_n_components}")
    print(f"threshold     = {best_threshold:.6f}")

    print_section("Test report")
    print(f"roc_auc = {roc_auc_score_binary(y_test, test_scores):.4f}")
    print(f"pr_auc  = {pr_auc_score_binary(y_test, test_scores):.4f}")
    print(f"precision = {prf['precision']:.4f}")
    print(f"recall    = {prf['recall']:.4f}")
    print(f"f1        = {prf['f1']:.4f}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(test_scores[y_test == 0], bins=20, alpha=0.7, label="normal")
    ax.hist(test_scores[y_test == 1], bins=20, alpha=0.7, label="anomaly")
    ax.axvline(best_threshold, color="black", linestyle="--", label="threshold")
    ax.set_title("PCA Reconstruction Error")
    ax.set_xlabel("squared error")
    ax.set_ylabel("count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "pca_anomaly_histogram.pdf")
    plt.close(fig)

    print(f"Saved figure: {RESULTS_DIR / 'pca_anomaly_histogram.pdf'}")


if __name__ == "__main__":
    main()
