"""
tools/vector_store.py — FAISS-based vector store for agent memory.
Stores and retrieves past research using semantic similarity search.
"""
from __future__ import annotations
import json
import os
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger


class VectorStore:
    """
    Simple FAISS vector store with sentence-transformer embeddings.
    Stores documents (research findings, reports) and enables semantic search.
    """

    def __init__(self, store_path: str = "./memory/vector_store"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.store_path / "faiss.index"
        self.meta_path = self.store_path / "metadata.json"
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.embedder = None
        self._load()

    def _get_embedder(self):
        if self.embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("[VectorStore] Embedder loaded")
            except Exception as e:
                logger.warning(f"[VectorStore] Could not load embedder: {e}")
        return self.embedder

    def _load(self):
        """Load existing index and metadata from disk."""
        try:
            if self.index_path.exists() and self.meta_path.exists():
                import faiss
                self.index = faiss.read_index(str(self.index_path))
                with open(self.meta_path) as f:
                    self.metadata = json.load(f)
                logger.info(f"[VectorStore] Loaded {len(self.metadata)} documents")
        except Exception as e:
            logger.warning(f"[VectorStore] Load failed (will start fresh): {e}")

    def _save(self):
        """Persist index and metadata to disk."""
        try:
            import faiss
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            with open(self.meta_path, "w") as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"[VectorStore] Save failed: {e}")

    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Embed and store a document."""
        try:
            import faiss
            import numpy as np
            embedder = self._get_embedder()
            if embedder is None:
                return False

            embedding = embedder.encode([content], convert_to_numpy=True).astype("float32")

            if self.index is None:
                dim = embedding.shape[1]
                self.index = faiss.IndexFlatL2(dim)

            self.index.add(embedding)
            self.metadata.append({
                "content": content[:1000],  # store preview
                "full_content": content,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {}),
            })
            self._save()
            logger.debug(f"[VectorStore] Added document. Total: {len(self.metadata)}")
            return True
        except Exception as e:
            logger.warning(f"[VectorStore] add_document failed: {e}")
            return False

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity."""
        try:
            import numpy as np
            embedder = self._get_embedder()
            if embedder is None or self.index is None or len(self.metadata) == 0:
                return []

            query_embedding = embedder.encode([query], convert_to_numpy=True).astype("float32")
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.metadata)))

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    doc = self.metadata[idx].copy()
                    doc["similarity_score"] = float(1 / (1 + dist))
                    results.append(doc)
            return results
        except Exception as e:
            logger.warning(f"[VectorStore] search failed: {e}")
            return []

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """Return the n most recent documents."""
        return self.metadata[-n:][::-1]

    def count(self) -> int:
        return len(self.metadata)

    def clear(self):
        """Clear all stored documents."""
        self.index = None
        self.metadata = []
        if self.index_path.exists():
            self.index_path.unlink()
        if self.meta_path.exists():
            self.meta_path.unlink()
        logger.info("[VectorStore] Cleared all documents")
