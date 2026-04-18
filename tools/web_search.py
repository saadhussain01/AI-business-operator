from __future__ import annotations
from typing import List, Dict, Any
from loguru import logger

def search_web(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({"title": r.get("title",""), "url": r.get("href",""), "snippet": r.get("body","")})
        logger.info(f"[WebSearch] '{query}' → {len(results)} results")
        return results
    except Exception as e:
        logger.warning(f"[WebSearch] failed: {e}")
        return []

def search_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({"title": r.get("title",""), "url": r.get("url",""),
                                 "snippet": r.get("body",""), "date": r.get("date",""), "source": r.get("source","")})
        return results
    except Exception as e:
        logger.warning(f"[NewsSearch] failed: {e}")
        return []

def format_search_results(results: List[Dict[str, Any]]) -> str:
    if not results: return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines += [f"[{i}] {r.get('title','')}", f"    URL: {r.get('url','')}", f"    {r.get('snippet','')}", ""]
    return "\n".join(lines)
