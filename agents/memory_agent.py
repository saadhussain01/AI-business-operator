"""
agents/memory_agent.py — Memory Agent
Stores completed research and reports in the vector store,
and retrieves relevant past knowledge to enrich future tasks.
"""
from __future__ import annotations
from typing import Dict, Any, List
from .base_agent import BaseAgent
from tools.vector_store import VectorStore


class MemoryAgent(BaseAgent):
    name = "MemoryAgent"
    description = "Stores and retrieves business knowledge from vector memory"

    def __init__(self, store_path: str = "./memory/vector_store"):
        super().__init__()
        self.store = VectorStore(store_path=store_path)
        self._log(f"Memory store loaded with {self.store.count()} documents")

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieve relevant past knowledge for a task."""
        context = context or {}
        action = context.get("action", "retrieve")  # "retrieve" or "store"

        if action == "store":
            return self._store(task, context)
        else:
            return self._retrieve(task)

    def _retrieve(self, task: str) -> Dict[str, Any]:
        """Find relevant past research for this task."""
        self._log(f"Searching memory for: '{task[:50]}'")
        results = self.store.search(task, top_k=3)

        if results:
            self._log(f"Found {len(results)} relevant memory documents")
            memory_text = "\n\n---\n\n".join([
                f"[Past Research - Score: {r['similarity_score']:.2f}]\n"
                f"Date: {r.get('timestamp', 'unknown')}\n"
                f"{r.get('full_content', r.get('content', ''))[:800]}"
                for r in results
            ])
        else:
            self._log("No relevant memory found")
            memory_text = ""

        return {
            "agent": self.name,
            "output": memory_text,
            "memory_hits": len(results),
            "results": results,
        }

    def _store(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Store completed research and report in memory."""
        content_to_store = []

        if context.get("research_output"):
            content_to_store.append(("research", context["research_output"]))
        if context.get("analysis_output"):
            content_to_store.append(("analysis", context["analysis_output"]))
        if context.get("final_report"):
            content_to_store.append(("report", context["final_report"]))

        stored = 0
        for doc_type, content in content_to_store:
            success = self.store.add_document(
                content=content,
                metadata={
                    "task": task,
                    "type": doc_type,
                    "task_type": context.get("task_type", "unknown"),
                },
            )
            if success:
                stored += 1

        self._log(f"Stored {stored} documents in memory. Total: {self.store.count()}")

        return {
            "agent": self.name,
            "output": f"Stored {stored} documents in memory",
            "documents_stored": stored,
            "total_memory": self.store.count(),
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": self.store.count(),
            "recent": self.store.get_recent(3),
        }
