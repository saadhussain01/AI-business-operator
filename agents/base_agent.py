"""
agents/base_agent.py — Base class for all agents in the system.
Handles LLM initialization, prompting, and response parsing.
Default provider: Google Gemini (free tier).
"""
from __future__ import annotations
import os
from typing import Optional, Dict, Any
from loguru import logger
from config.settings import settings


def get_llm_response(
    system_prompt: str,
    user_message: str,
    max_tokens: int = None,
    temperature: float = 0.3,
) -> str:
    """
    Call the configured LLM and return the text response.
    Priority: Gemini (free) → Anthropic → mock fallback.
    """
    max_tokens = max_tokens or settings.MAX_TOKENS_PER_AGENT

    # ── Google Gemini (default — free tier) ───────────────────────────────
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )

            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=generation_config,
                system_instruction=system_prompt,
            )

            response = model.generate_content(user_message)
            return response.text

        except Exception as e:
            logger.error(f"[LLM/Gemini] {e}")
            return f"[Gemini API error: {e}]"

    # ── Anthropic Claude (optional fallback) ──────────────────────────────
    if settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return msg.content[0].text
        except Exception as e:
            logger.error(f"[LLM/Anthropic] {e}")
            return f"[Anthropic API error: {e}]"

    # ── Mock fallback (no API key set) ────────────────────────────────────
    logger.warning("[LLM] No API key configured — returning mock response")
    return (
        "⚠️  No LLM API key configured.\n\n"
        "Please set GEMINI_API_KEY in your .env file.\n"
        "Get a FREE Gemini API key at: https://aistudio.google.com/apikey\n\n"
        f"System prompt preview: {system_prompt[:100]}...\n"
        f"User message: {user_message[:200]}"
    )


class BaseAgent:
    """Abstract base class for all business operator agents."""

    name: str = "BaseAgent"
    description: str = ""

    def __init__(self):
        logger.info(f"[{self.name}] Initialized")

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def _call_llm(self, system_prompt: str, user_message: str, **kwargs) -> str:
        logger.debug(f"[{self.name}] Calling LLM ({settings.LLM_PROVIDER})...")
        return get_llm_response(system_prompt, user_message, **kwargs)

    def _log(self, msg: str):
        logger.info(f"[{self.name}] {msg}")
