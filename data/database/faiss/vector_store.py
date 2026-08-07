from __future__ import annotations

from pathlib import Path

import numpy as np

from .faiss_manager import FAISSManager


class VectorStore:
    """High-level vector store abstraction on top of FAISSManager."""

    def __init__(self, dimension: int = 768, index_path: str | Path | None = None) -> None:
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else Path(__file__).with_name("vehicle.index")
        self.manager = FAISSManager(dimension=dimension)
        self._load_existing()

    def _load_existing(self) -> None:
        self.manager.load_index(self.index_path)

    def reset(self) -> None:
        self.manager.create_index()
        if self.index_path.exists():
            self.index_path.unlink()

        npy_fallback = self.index_path.with_suffix(".npy")
        if npy_fallback.exists():
            npy_fallback.unlink()

    def add(self, vectors: np.ndarray) -> int:
        vector_id = self.manager.count()
        self.manager.add_vectors(vectors)
        return vector_id

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        return self.manager.search(query_vector=query_vector, top_k=top_k)

    def save(self) -> None:
        self.manager.save_index(self.index_path)

    def count(self) -> int:
        return self.manager.count()

    def get_dimension(self) -> int:
        return self.dimension