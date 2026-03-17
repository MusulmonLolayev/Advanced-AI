"""Optional anomaly-detection extension using k-th neighbor distance."""

from __future__ import annotations

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.config import ANOMALY_DATA_PATH, CORE_METRICS, K_CHOICES
from advanced_ai.data_utils import load_anomaly_bundle
from advanced_ai.metrics import best_f1_threshold, pr_auc_score_binary, roc_auc_score_binary
from advanced_ai.task_utils import print_section, require_file


def main() -> None:
    bundle = load_anomaly_bundle(require_file(ANOMALY_DATA_PATH))
    model = KNearestNeighbor()
    model.fit(bundle["X_train"])

    best = None
    for metric in CORE_METRICS:
        for k in K_CHOICES:
            val_scores = model.anomaly_scores(bundle["X_val"], k=k, metric=metric)
            val_roc = roc_auc_score_binary(bundle["y_val"], val_scores)
            val_pr = pr_auc_score_binary(bundle["y_val"], val_scores)
            threshold, threshold_f1 = best_f1_threshold(bundle["y_val"], val_scores)
            row = {
                "k": k,
                "metric": metric,
                "val_roc_auc": val_roc,
                "val_pr_auc": val_pr,
                "threshold": threshold,
                "threshold_f1": threshold_f1,
            }
            print(row)
            if best is None or row["val_pr_auc"] > best["val_pr_auc"]:
                best = row

    test_scores = model.anomaly_scores(bundle["X_test"], k=best["k"], metric=best["metric"])
    test_roc = roc_auc_score_binary(bundle["y_test"], test_scores)
    test_pr = pr_auc_score_binary(bundle["y_test"], test_scores)

    print_section("\nBest validation config")
    print(best)
    print_section("\nTest report")
    print(f"ROC-AUC = {test_roc:.4f}")
    print(f"PR-AUC  = {test_pr:.4f}")
    print(f"threshold_from_validation = {best['threshold']:.6f}")


if __name__ == "__main__":
    main()
