from __future__ import annotations
import re
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from typing import Optional

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def scrape_url(url: str, max_chars: int = 4000) -> Optional[str]:
    try:
        with httpx.Client(timeout=12, headers=HEADERS, follow_redirects=True) as c:
            resp = c.get(url); resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script","style","nav","footer","header","aside","form","iframe"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()
        return text[:max_chars] + ("..." if len(text) > max_chars else "")
    except Exception as e:
        logger.warning(f"[Scraper] {url}: {e}"); return None
