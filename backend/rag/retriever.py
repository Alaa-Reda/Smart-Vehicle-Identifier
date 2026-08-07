"""
Retriever
=========
Handles vector similarity search over FAISS and MongoDB mapping.

Responsibilities:
- Convert text to embeddings using a sentence transformer.
- Query FAISS for nearest-neighbor vector IDs.
- Map vector IDs back to MongoDB documents.
- Add new documents to the FAISS index.
- Rebuild the FAISS index.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from itsdangerous import exc
import numpy as np

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768


@dataclass
class RetrievedDocument:
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None


class Retriever:
    """
    Semantic document retriever backed by FAISS + sentence-transformers.
    """

    _embedding_model = None   # Loaded lazily to avoid startup latency
    _vector_store = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def retrieve(
        self, query: str, top_k: int = 10
    ) -> List[RetrievedDocument]:
        """
        Encode `query` and search for the top-k most similar documents.
        """
        if not query.strip():
            return []

        try:
            embedding = await self._embed(query)
            store = await self._get_vector_store()
            scores, indices = store.search(embedding, top_k=top_k)
            return await self._resolve_documents(scores, indices)
        except Exception as exc:
            logger.warning("Retrieval failed: %s", exc)
            return []

    async def add_document(
        self, text: str, metadata: Dict[str, Any]
    ) -> Optional[int]:
        """
        Embed `text` and add it to the FAISS index.
        Returns the assigned vector ID, or None on failure.
        """
        if not text.strip():
            return None

        try:
            embedding = await self._embed(text)
            store = await self._get_vector_store()

            async with self._lock:
                vector_id = store.add(embedding)
                store.save()

            await self._store_vector_mapping(
                vector_id=vector_id,
                text=text,
                metadata=metadata,
            )
            return vector_id
        except Exception as exc:
            logger.warning("Failed to add document to FAISS: %s", exc)
            return None

    async def rebuild_index(self) -> None:
        """
        Rebuild the FAISS index from all documents in MongoDB.
        """
        try:
            store = await self._get_vector_store()
            async with self._lock:
                store.reset()

            documents = await self._load_all_documents()
            for doc in documents:
                await self.add_document(
                    text=doc.get("content", ""),
                    metadata=doc.get("metadata", {}),
                )
            logger.info("Index rebuilt with %d documents.", len(documents))
        except Exception as exc:
            logger.error("Index rebuild failed: %s", exc)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    async def _embed(self, text: str) -> np.ndarray:
        model = await self._get_embedding_model()
        loop = asyncio.get_event_loop()
        vector = await loop.run_in_executor(
            None, lambda: model.encode([text], normalize_embeddings=True)
        )
        return vector.astype(np.float32)

    async def _get_embedding_model(self):
        if self._embedding_model is None:
            async with self._lock:
                if self._embedding_model is None:
                    from sentence_transformers import SentenceTransformer  # type: ignore
                    self.__class__._embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedding_model

    async def _get_vector_store(self):
        if self._vector_store is None:
            async with self._lock:
                if self._vector_store is None:
                    try:
                        from data.database.faiss.vector_store import VectorStore  # type: ignore
                        self.__class__._vector_store = VectorStore(dimension=EMBEDDING_DIM)
                    except Exception as exc:
                        logger.exception("Failed to initialize VectorStore: %s", exc)
                        raise
        return self._vector_store

    async def _resolve_documents(
        self,
        scores: Any,
        indices: Any,
    ) -> List[RetrievedDocument]:
        results: List[RetrievedDocument] = []
        flat_scores = scores.flatten().tolist()
        flat_indices = indices.flatten().tolist()

        logger.info("FAISS indices: %s", flat_indices)
        logger.info("FAISS scores : %s", flat_scores)

        for score, idx in zip(flat_scores, flat_indices):

            logger.info("Checking vector_id=%s", idx)

            if idx < 0:
                continue

            doc = await self._fetch_document_by_vector_id(int(idx))

            logger.info("MongoDB document = %s", doc)

            if doc:
                results.append(
                    RetrievedDocument(
                        content=doc.get("content", ""),
                        score=float(score),
                        metadata=doc.get("metadata", {}),
                        doc_id=doc.get("_id"),
                    )
                )

        return results

    async def _fetch_document_by_vector_id(
        self, vector_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            from data.database.mongodb.vector_index import VectorIndexCollection  # type: ignore
            loop = asyncio.get_event_loop()
            vic = VectorIndexCollection()
            return await loop.run_in_executor(None, vic.find_by_vector_id, vector_id)
        except Exception as exc:
            logger.warning("Vector ID %d lookup failed: %s", vector_id, exc)
            return None

    async def _store_vector_mapping(
        self, vector_id: int, text: str, metadata: Dict[str, Any]
    ) -> None:
        try:
            from data.database.mongodb.vector_index import VectorIndexCollection  # type: ignore
            loop = asyncio.get_event_loop()
            vic = VectorIndexCollection()
            await loop.run_in_executor(
                None,
                vic.insert,
                {
                    "vector_id": vector_id,
                    "content": text,
                    "metadata": metadata,
                },
            )
        except Exception as exc:
            logger.warning("Failed to store vector mapping: %s", exc)

    async def _load_all_documents(self) -> List[Dict[str, Any]]:
        try:
            from data.database.mongodb.vector_index import VectorIndexCollection  # type: ignore
            loop = asyncio.get_event_loop()
            vic = VectorIndexCollection()
            return await loop.run_in_executor(None, vic.find_all) or []
        except Exception as exc:
            logger.warning("Failed to load documents from MongoDB: %s", exc)
            return []
