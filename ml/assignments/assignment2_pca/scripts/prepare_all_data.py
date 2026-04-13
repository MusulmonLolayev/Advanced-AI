"""Single entrypoint to prepare all PCA datasets used by the assignment."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--core-only", action="store_true")
    parser.add_argument("--skip-embeddings", action="store_true")
    parser.add_argument("--skip-anomaly", action="store_true")
    args = parser.parse_args()

    from prepare_pca_anomaly import prepare_pca_anomaly_dataset
    from prepare_pca_core import prepare_pca_core_dataset, prepare_pca_knn_comparison_dataset
    from prepare_pca_embeddings import prepare_pca_text_embeddings

    print("Preparing core PCA datasets")
    core_path = prepare_pca_core_dataset(overwrite=args.overwrite)
    knn_path = prepare_pca_knn_comparison_dataset(overwrite=args.overwrite)
    print(f"Saved: {core_path}")
    print(f"Saved: {knn_path}")

    if args.core_only:
        return

    if not args.skip_embeddings:
        print("Preparing text embedding data")
        embeddings_path = prepare_pca_text_embeddings(overwrite=args.overwrite)
        print(f"Saved: {embeddings_path}")

    if not args.skip_anomaly:
        print("Preparing anomaly dataset")
        anomaly_path = prepare_pca_anomaly_dataset(overwrite=args.overwrite)
        print(f"Saved: {anomaly_path}")


if __name__ == "__main__":
    main()
