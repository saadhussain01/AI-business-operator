"""
agents/base_agent.py — Base class using the new google-genai SDK.
The old google-generativeai package is deprecated; this uses google-genai >= 1.0.
"""
from __future__ import annotations
from typing import Dict, Any
from loguru import logger
from config.settings import settings


def get_llm_response(
    system_prompt: str,
    user_message: str,
    max_tokens: int = None,
    temperature: float = 0.3,
) -> str:
    max_tokens = max_tokens or settings.MAX_TOKENS_PER_AGENT

    # ── Google Gemini (new SDK: google-genai) ─────────────────────────────
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text

        except Exception as e:
            logger.error(f"[LLM/Gemini] {e}")
            return f"[Gemini error: {e}]"

    # ── Anthropic Claude (fallback) ────────────────────────────────────────
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
            return f"[Anthropic error: {e}]"

    # ── No key configured ─────────────────────────────────────────────────
    logger.warning("[LLM] No API key — returning mock")
    return (
        "⚠️ No API key configured.\n\n"
        "Set GEMINI_API_KEY in your .env file.\n"
        "Get a FREE key at: https://aistudio.google.com/apikey\n\n"
        f"Message preview: {user_message[:150]}"
    )


class BaseAgent:
    name: str = "BaseAgent"
    description: str = ""

    def __init__(self):
        logger.info(f"[{self.name}] Initialized")

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def _call_llm(self, system_prompt: str, user_message: str, **kwargs) -> str:
        logger.debug(f"[{self.name}] Calling {settings.LLM_PROVIDER}...")
        return get_llm_response(system_prompt, user_message, **kwargs)

    def _log(self, msg: str):
        logger.info(f"[{self.name}] {msg}")
