from __future__ import annotations
from typing import Dict, Any
from .base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    name = "MemoryAgent"
    description = "Stores/retrieves knowledge from FAISS vector store"

    def __init__(self, store_path: str = "./memory/vector_store"):
        super().__init__()
        try:
            from tools.vector_store import VectorStore
            self.store = VectorStore(store_path=store_path)
            self._log(f"Loaded {self.store.count()} docs")
        except Exception as e:
            self._log(f"Vector store unavailable: {e}")
            self.store = None

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        if context.get("action") == "store":
            return self._store(task, context)
        return self._retrieve(task)

    def _retrieve(self, task: str) -> Dict[str, Any]:
        if not self.store:
            return {"agent": self.name, "output": "", "memory_hits": 0}
        results = self.store.search(task, top_k=3)
        text = "\n\n---\n\n".join([
            f"[Past Research – Score {r['similarity_score']:.2f}]\n{r.get('full_content', r.get('content',''))[:600]}"
            for r in results
        ]) if results else ""
        return {"agent": self.name, "output": text, "memory_hits": len(results)}

    def _store(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.store:
            return {"agent": self.name, "output": "Vector store unavailable", "documents_stored": 0}
        stored = 0
        for key in ("research_output", "analysis_output", "final_report"):
            if context.get(key):
                if self.store.add_document(context[key], {"task": task, "type": key}):
                    stored += 1
        return {"agent": self.name, "output": f"Stored {stored} docs", "documents_stored": stored}

    def get_stats(self) -> Dict[str, Any]:
        if not self.store:
            return {"total_documents": 0, "recent": []}
        return {"total_documents": self.store.count(), "recent": self.store.get_recent(3)}
