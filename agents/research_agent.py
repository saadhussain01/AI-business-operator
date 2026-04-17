"""
agents/research_agent.py — Market Research Agent
Searches the web, scrapes relevant content, and synthesizes findings
into structured research data for the Analysis Agent.
"""
from __future__ import annotations
from typing import Dict, Any, List
from .base_agent import BaseAgent
from tools.web_search import search_web, search_news, format_search_results
from tools.scraper import scrape_url
from loguru import logger


RESEARCH_SYSTEM = """You are the Research Agent in an autonomous AI Business Operator system.
You receive raw web search results and extract the most relevant, factual information.

Your job:
1. Identify key companies, statistics, market data, and trends
2. Extract specific numbers (market sizes, growth rates, revenue figures)
3. Note the most credible sources
4. Summarize findings clearly and factually

Structure your response as:
## Key Findings
[bullet points of most important discoveries]

## Market Data & Statistics
[specific numbers and metrics found]

## Key Players / Companies
[list with brief descriptions]

## Recent Developments
[latest news and trends]

## Source Quality Notes
[assessment of source credibility]

Be concise, specific, and data-driven. Cite specific figures when available."""


class ResearchAgent(BaseAgent):
    name = "ResearchAgent"
    description = "Searches the web and synthesizes market research data"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        plan = context.get("plan", {})
        search_queries = plan.get("search_queries", [task])

        if not search_queries:
            search_queries = [task]

        self._log(f"Running {len(search_queries)} search queries...")

        all_results = []
        news_results = []

        # Execute each search query from the planner
        for query in search_queries[:4]:
            self._log(f"Searching: '{query}'")
            results = search_web(query, max_results=6)
            all_results.extend(results)

        # Also search for recent news
        news_query = search_queries[0] if search_queries else task
        news = search_news(news_query, max_results=4)
        news_results.extend(news)

        # Optionally scrape top result for deeper content
        deep_content = ""
        if all_results:
            top_url = all_results[0].get("url", "")
            if top_url:
                self._log(f"Deep-scraping top result: {top_url}")
                scraped = scrape_url(top_url, max_chars=3000)
                if scraped:
                    deep_content = f"\n\n[Deep Content from {top_url}]:\n{scraped}"

        # Format all results for LLM
        formatted_web = format_search_results(all_results[:10])
        formatted_news = format_search_results(news_results)

        full_context = f"""
TASK: {task}

WEB SEARCH RESULTS:
{formatted_web}

RECENT NEWS:
{formatted_news}
{deep_content}
"""

        self._log("Synthesizing research findings with LLM...")
        synthesis = self._call_llm(
            system_prompt=RESEARCH_SYSTEM,
            user_message=full_context,
            max_tokens=1200,
        )

        return {
            "agent": self.name,
            "output": synthesis,
            "raw_results": all_results,
            "news_results": news_results,
            "queries_used": search_queries,
            "sources_count": len(all_results),
        }
