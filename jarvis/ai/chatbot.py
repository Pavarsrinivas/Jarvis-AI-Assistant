"""
chatbot.py
----------
General-purpose conversational fallback, backed by the OpenAI Chat
Completions API. Used by the Router whenever a command doesn't match
any specific skill.

Conversation context is pulled from the Memory module so the chatbot
has continuity across turns within the configured window.
"""

import logging
from typing import List, Dict

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS,
    SYSTEM_PROMPT,
)

logger = logging.getLogger("jarvis.ai.chatbot")

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None
    logger.warning(
        "openai package is not installed. Run 'pip install openai' to "
        "enable conversational responses."
    )


class Chatbot:
    """Thin wrapper around the OpenAI Chat Completions API with memory context."""

    def __init__(self, memory, model: str = OPENAI_MODEL):
        self.memory = memory
        self.model = model
        self._client = None

        if OpenAI and OPENAI_API_KEY:
            self._client = OpenAI(api_key=OPENAI_API_KEY)
        elif OpenAI and not OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY is not set. The chatbot will return a "
                "placeholder response until a key is configured."
            )

    def _build_messages(self, user_text: str) -> List[Dict[str, str]]:
        """Combine the system prompt, recent memory, and the new message."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for turn in self.memory.recent(n=6):
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        messages.append({"role": "user", "content": user_text})
        return messages

    def ask(self, user_text: str) -> str:
        """Send `user_text` to the LLM and return its reply as plain text."""
        if not self._client:
            return (
                "I can't reach my language model right now — please set "
                "OPENAI_API_KEY in your environment or .env file."
            )

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(user_text),
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.exception("Chatbot request failed: %s", exc)
            return "Sorry, I had trouble reaching the language model just now."
