"""
tools/web_search.py — Web search tool using DuckDuckGo (free, no API key needed)
Falls back to SerpAPI if key is configured.
"""
from __future__ import annotations
import time
from typing import List, Dict, Any
from loguru import logger


def search_web(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search the web for a query. Returns a list of result dicts with
    keys: title, url, snippet.
    Uses DuckDuckGo by default (no API key required).
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        logger.info(f"[WebSearch] '{query}' → {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"[WebSearch] DuckDuckGo failed: {e}. Returning empty.")
        return []


def search_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search for recent news articles."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("body", ""),
                    "date": r.get("date", ""),
                    "source": r.get("source", ""),
                })
        logger.info(f"[NewsSearch] '{query}' → {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"[NewsSearch] failed: {e}")
        return []


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results into readable text for LLM consumption."""
    if not results:
        return "No search results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title', 'No title')}")
        lines.append(f"    URL: {r.get('url', '')}")
        lines.append(f"    {r.get('snippet', '')}")
        if r.get("date"):
            lines.append(f"    Date: {r['date']}")
        lines.append("")
    return "\n".join(lines)
