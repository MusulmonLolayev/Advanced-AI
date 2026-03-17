"""End-to-end retrieval dataset download and embedding generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import DATASETS_DIR, RAW_DIR, download_file, ensure_dir, simple_token_length, unzip_file


BEIR_SCIFACT_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _load_scifact_dataset(overwrite: bool = False):
    from beir.datasets.data_loader import GenericDataLoader

    archive_path = download_file(BEIR_SCIFACT_URL, RAW_DIR / "scifact.zip", overwrite=overwrite)
    extract_dir = unzip_file(archive_path, RAW_DIR / "scifact", overwrite=overwrite)
    data_dir = extract_dir / "scifact"
    if not data_dir.exists():
        data_dir = extract_dir
    corpus, queries, qrels = GenericDataLoader(data_folder=str(data_dir)).load(split="test")
    return corpus, queries, qrels


def _encode_texts(texts: list[str], model_name: str, batch_size: int) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    return model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )


def prepare_text_retrieval_embeddings(
    model_name: str = DEFAULT_MODEL,
    batch_size: int = 64,
    overwrite: bool = False,
) -> Path:
    ensure_dir(DATASETS_DIR)
    out_path = DATASETS_DIR / "text_retrieval_embeddings.npz"
    if out_path.exists() and not overwrite:
        return out_path

    corpus, queries, qrels = _load_scifact_dataset(overwrite=overwrite)

    doc_ids = sorted(corpus.keys())
    query_ids = sorted(queries.keys())

    doc_texts = []
    for doc_id in doc_ids:
        title = corpus[doc_id].get("title", "") or ""
        text = corpus[doc_id].get("text", "") or ""
        doc_texts.append((title + " " + text).strip())

    query_texts = [queries[query_id] for query_id in query_ids]
    doc_lengths = np.array([simple_token_length(text) for text in doc_texts], dtype=np.int32)
    query_lengths = np.array([simple_token_length(text) for text in query_texts], dtype=np.int32)

    doc_embeddings = _encode_texts(doc_texts, model_name=model_name, batch_size=batch_size)
    query_embeddings = _encode_texts(query_texts, model_name=model_name, batch_size=batch_size)

    doc_index = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}
    relevance = np.zeros((len(query_ids), len(doc_ids)), dtype=np.int8)
    for q_idx, query_id in enumerate(query_ids):
        for doc_id in qrels.get(query_id, {}):
            if doc_id in doc_index:
                relevance[q_idx, doc_index[doc_id]] = 1

    np.savez_compressed(
        out_path,
        query_embeddings=np.asarray(query_embeddings, dtype=np.float32),
        doc_embeddings=np.asarray(doc_embeddings, dtype=np.float32),
        relevance=relevance,
        query_lengths=query_lengths,
        doc_lengths=doc_lengths,
        query_ids=np.asarray(query_ids, dtype=object),
        doc_ids=np.asarray(doc_ids, dtype=object),
        model_name=np.asarray(model_name),
        dataset_name=np.asarray("scifact"),
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    out_path = prepare_text_retrieval_embeddings(
        model_name=args.model_name,
        batch_size=args.batch_size,
        overwrite=args.overwrite,
    )
    print(f"Saved retrieval embeddings to: {out_path}")


if __name__ == "__main__":
    main()
