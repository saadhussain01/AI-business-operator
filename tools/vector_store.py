from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger

class VectorStore:
    def __init__(self, store_path: str = "./memory/vector_store"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.store_path / "faiss.index"
        self.meta_path  = self.store_path / "metadata.json"
        self.index = None; self.metadata: List[Dict] = []; self.embedder = None
        self._load()

    def _embedder(self):
        if not self.embedder:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"[VectorStore] embedder unavailable: {e}")
        return self.embedder

    def _load(self):
        try:
            if self.index_path.exists() and self.meta_path.exists():
                import faiss
                self.index = faiss.read_index(str(self.index_path))
                self.metadata = json.loads(self.meta_path.read_text())
        except Exception as e:
            logger.warning(f"[VectorStore] load: {e}")

    def _save(self):
        try:
            import faiss
            if self.index: faiss.write_index(self.index, str(self.index_path))
            self.meta_path.write_text(json.dumps(self.metadata, indent=2, default=str))
        except Exception as e:
            logger.warning(f"[VectorStore] save: {e}")

    def add_document(self, content: str, metadata: Dict = None) -> bool:
        try:
            import faiss, numpy as np
            emb = self._embedder()
            if not emb: return False
            vec = emb.encode([content], convert_to_numpy=True).astype("float32")
            if self.index is None:
                self.index = faiss.IndexFlatL2(vec.shape[1])
            self.index.add(vec)
            self.metadata.append({"content": content[:800], "full_content": content,
                                   "timestamp": datetime.now().isoformat(), **(metadata or {})})
            self._save(); return True
        except Exception as e:
            logger.warning(f"[VectorStore] add: {e}"); return False

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        try:
            import numpy as np
            emb = self._embedder()
            if not emb or self.index is None or not self.metadata: return []
            vec = emb.encode([query], convert_to_numpy=True).astype("float32")
            dists, idxs = self.index.search(vec, min(top_k, len(self.metadata)))
            return [{**self.metadata[i], "similarity_score": float(1/(1+d))}
                    for d, i in zip(dists[0], idxs[0]) if 0 <= i < len(self.metadata)]
        except Exception as e:
            logger.warning(f"[VectorStore] search: {e}"); return []

    def get_recent(self, n: int = 5) -> List[Dict]: return self.metadata[-n:][::-1]
    def count(self) -> int: return len(self.metadata)
    def clear(self):
        self.index = None; self.metadata = []
        for p in (self.index_path, self.meta_path):
            if p.exists(): p.unlink()
