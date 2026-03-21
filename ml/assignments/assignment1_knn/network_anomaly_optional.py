"""Optional anomaly-detection extension using k-th neighbor distance."""

from __future__ import annotations

import argparse

from advanced_ai.classifiers.k_nearest_neighbor import KNearestNeighbor
from advanced_ai.config import ANOMALY_DATA_PATH, CORE_METRICS, K_CHOICES
from advanced_ai.data_utils import load_anomaly_bundle
from advanced_ai.metrics import best_f1_threshold, pr_auc_score_binary, roc_auc_score_binary
from advanced_ai.task_utils import print_section, require_file


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["l2"],
        help=f"Distance metrics to evaluate (supported: {', '.join(CORE_METRICS)}).",
    )
    parser.add_argument(
        "--num-loops",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Distance implementation mode forwarded to k-NN.",
    )
    parser.add_argument(
        "--allow-slow-l1",
        action="store_true",
        help="Allow L1 evaluation on full anomaly data (can be very slow).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    metrics = [metric.lower() for metric in args.metrics]
    invalid_metrics = sorted(set(metrics) - set(CORE_METRICS))
    if invalid_metrics:
        raise ValueError(f"Unsupported metrics requested: {invalid_metrics}. Allowed: {CORE_METRICS}")
    if "l1" in metrics and not args.allow_slow_l1:
        raise ValueError(
            "metric='l1' on the full anomaly dataset is intentionally blocked because "
            "it is extremely slow for brute-force k-NN. Use --allow-slow-l1 to run it "
            "anyway, or keep --metrics l2."
        )

    bundle = load_anomaly_bundle(require_file(ANOMALY_DATA_PATH))
    model = KNearestNeighbor()
    model.fit(bundle["X_train"])

    # Full vectorized L1 on this dataset allocates an enormous temporary tensor
    # and can OOM on typical laptops. Use one-loop for L1 unless explicitly
    # overridden with --num-loops 1/2 by the user.
    l1_num_loops = args.num_loops
    if args.num_loops == 0 and "l1" in metrics:
        l1_num_loops = 1
        print("Note: using num_loops=1 for metric=l1 to avoid excessive memory usage.")

    print_section("Validation sweep")
    best = None
    for metric in metrics:
        metric_num_loops = l1_num_loops if metric == "l1" else args.num_loops
        for k in K_CHOICES:
            val_scores = model.anomaly_scores(
                bundle["X_val"], k=k, metric=metric, num_loops=metric_num_loops
            )
            val_roc = roc_auc_score_binary(bundle["y_val"], val_scores)
            val_pr = pr_auc_score_binary(bundle["y_val"], val_scores)
            threshold, threshold_f1 = best_f1_threshold(bundle["y_val"], val_scores)
            row = {
                "k": k,
                "metric": metric,
                "num_loops": metric_num_loops,
                "val_roc_auc": val_roc,
                "val_pr_auc": val_pr,
                "threshold": threshold,
                "threshold_f1": threshold_f1,
            }
            print(row)
            if best is None or row["val_pr_auc"] > best["val_pr_auc"]:
                best = row

    test_scores = model.anomaly_scores(
        bundle["X_test"],
        k=best["k"],
        metric=best["metric"],
        num_loops=best["num_loops"],
    )
    test_roc = roc_auc_score_binary(bundle["y_test"], test_scores)
    test_pr = pr_auc_score_binary(bundle["y_test"], test_scores)

    print_section("Best validation config")
    print(best)
    print_section("Test report")
    print(f"ROC-AUC = {test_roc:.4f}")
    print(f"PR-AUC  = {test_pr:.4f}")
    print(f"threshold_from_validation = {best['threshold']:.6f}")


if __name__ == "__main__":
    main()
