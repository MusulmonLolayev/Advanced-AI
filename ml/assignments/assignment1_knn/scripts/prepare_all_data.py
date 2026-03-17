"""Single entrypoint to prepare all datasets and optional assets."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--core-only", action="store_true")
    parser.add_argument("--skip-retrieval", action="store_true")
    parser.add_argument("--skip-anomaly", action="store_true")
    parser.add_argument("--model-name", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args()

    from prepare_core_datasets import prepare_banknote_dataset, prepare_california_dataset
    from prepare_network_anomaly import prepare_network_anomaly_dataset
    from prepare_text_retrieval_embeddings import prepare_text_retrieval_embeddings

    print("Preparing core datasets")
    banknote_path = prepare_banknote_dataset(overwrite=args.overwrite)
    california_path = prepare_california_dataset(overwrite=args.overwrite)
    print(f"Saved: {banknote_path}")
    print(f"Saved: {california_path}")

    if args.core_only:
        return

    if not args.skip_retrieval:
        print("Preparing retrieval embeddings")
        retrieval_path = prepare_text_retrieval_embeddings(
            model_name=args.model_name,
            batch_size=args.batch_size,
            overwrite=args.overwrite,
        )
        print(f"Saved: {retrieval_path}")

    if not args.skip_anomaly:
        print("Preparing anomaly dataset")
        anomaly_path = prepare_network_anomaly_dataset(overwrite=args.overwrite)
        print(f"Saved: {anomaly_path}")


if __name__ == "__main__":
    main()
