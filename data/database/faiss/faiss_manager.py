from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - runtime dependent
    faiss = None


class _NumpyIndex:
    """Small FAISS-like fallback for environments without faiss."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.vectors = np.empty((0, dimension), dtype=np.float32)

    @property
    def ntotal(self) -> int:
        return int(self.vectors.shape[0])

    def add(self, vectors: np.ndarray) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected vectors with shape (n, {self.dimension}), got {vectors.shape}."
            )
        self.vectors = np.vstack([self.vectors, vectors])

    def search(self, query: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        if self.ntotal == 0:
            return (
                np.full((1, top_k), np.inf, dtype=np.float32),
                np.full((1, top_k), -1, dtype=np.int64),
            )

        distances = np.sum((self.vectors - query) ** 2, axis=1)
        sorted_idx = np.argsort(distances)
        top_idx = sorted_idx[:top_k]

        scores = np.full(top_k, np.inf, dtype=np.float32)
        indices = np.full(top_k, -1, dtype=np.int64)

        scores[: len(top_idx)] = distances[top_idx]
        indices[: len(top_idx)] = top_idx

        return scores.reshape(1, -1), indices.reshape(1, -1)


class FAISSManager:
    """Low-level manager for vector index operations."""

    def __init__(self, dimension: int = 768) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be a positive integer.")

        self.dimension = dimension
        self.index = None
        self.create_index()

    def create_index(self) -> None:
        if faiss is not None:
            self.index = faiss.IndexFlatL2(self.dimension)
            return

        self.index = _NumpyIndex(self.dimension)

    def add_vectors(self, vectors: np.ndarray) -> None:
        if self.index is None:
            self.create_index()

        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected vectors with shape (n, {self.dimension}), got {vectors.shape}."
            )

        self.index.add(vectors)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        if self.index is None:
            self.create_index()

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query = np.asarray(query_vector, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Expected query vector dimension {self.dimension}, got {query.shape[1]}."
            )

        scores, indices = self.index.search(query, top_k)
        return scores[0], indices[0]

    def count(self) -> int:
        if self.index is None:
            return 0
        return int(self.index.ntotal)

    def save_index(self, index_path: str | Path) -> None:
        if self.index is None:
            self.create_index()

        path = Path(index_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if faiss is not None and hasattr(self.index, "is_trained"):
            faiss.write_index(self.index, str(path))
            return

        np.save(path.with_suffix(".npy"), self.index.vectors)

    def load_index(self, index_path: str | Path) -> bool:
        path = Path(index_path)
        if not path.exists() and not path.with_suffix(".npy").exists():
            return False

        if faiss is not None and path.exists():
            self.index = faiss.read_index(str(path))
            return True

        vectors = np.load(path.with_suffix(".npy")).astype(np.float32)
        self.index = _NumpyIndex(self.dimension)
        if len(vectors) > 0:
            self.index.add(vectors)
        return True