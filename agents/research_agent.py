from __future__ import annotations
from typing import Dict, Any
from .base_agent import BaseAgent

RESEARCH_SYSTEM = """You are the Research Agent in an autonomous AI Business Operator.
Synthesise raw web search results into structured research findings.

Format:
## Key Findings
[bullet points of most important facts]

## Market Data & Statistics
[specific numbers, percentages, market sizes]

## Key Players / Companies
[list with brief descriptions]

## Recent Developments
[latest news and trends]

Be concise, specific, and data-driven."""

class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    description = "Searches the web and synthesises research data"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        plan = context.get("plan", {})
        queries = plan.get("search_queries", [task])[:4]
        self._log(f"Running {len(queries)} searches…")

        all_results, news_results = [], []
        try:
            from tools.web_search import search_web, search_news, format_search_results
            for q in queries:
                all_results.extend(search_web(q, max_results=5))
            news_results = search_news(queries[0], max_results=4)
            web_text  = format_search_results(all_results[:10])
            news_text = format_search_results(news_results)
        except Exception as e:
            self._log(f"Search error: {e}")
            web_text = news_text = "Search unavailable."

        prompt = f"TASK: {task}\n\nWEB RESULTS:\n{web_text}\n\nNEWS:\n{news_text}"
        synthesis = self._call_llm(RESEARCH_SYSTEM, prompt, max_tokens=1200)
        return {
            "agent": self.name, "output": synthesis,
            "sources_count": len(all_results),
            "queries_used": queries,
        }
