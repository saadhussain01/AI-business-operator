"""
tools/scraper.py — Lightweight web scraper to extract full page text
"""
from __future__ import annotations
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from typing import Optional


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_url(url: str, max_chars: int = 4000) -> Optional[str]:
    """
    Fetch and parse text content from a URL.
    Returns cleaned text or None on failure.
    """
    try:
        with httpx.Client(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise elements
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "form", "iframe", "noscript"]):
            tag.decompose()

        # Extract meaningful text
        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        import re
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        logger.debug(f"[Scraper] {url} → {len(text)} chars")
        return text

    except Exception as e:
        logger.warning(f"[Scraper] Failed to scrape {url}: {e}")
        return None


def scrape_multiple(urls: list[str], max_per_page: int = 2000) -> dict[str, str]:
    """Scrape multiple URLs and return a dict of url → text."""
    results = {}
    for url in urls[:5]:  # limit to 5 to avoid slowdowns
        text = scrape_url(url, max_chars=max_per_page)
        if text:
            results[url] = text
    return results
