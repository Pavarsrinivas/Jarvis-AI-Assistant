"""
memory.py
---------
Manages JARVIS's conversation history and context memory. Keeps an
in-memory list of {"user", "assistant"} turns for the current session,
and persists it to `data/memory.json` so context can survive restarts.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List

from config import MEMORY_FILE_PATH, MAX_MEMORY_MESSAGES

logger = logging.getLogger("jarvis.core.memory")


class Memory:
    """Stores and persists conversational turns between the user and JARVIS."""

    def __init__(self, file_path: str = MEMORY_FILE_PATH, max_messages: int = MAX_MEMORY_MESSAGES):
        self.file_path = file_path
        self.max_messages = max_messages
        self.history: List[Dict[str, str]] = []
        self._load()

    def _load(self) -> None:
        """Load conversation history from disk, if it exists."""
        if not os.path.exists(self.file_path):
            logger.info("No existing memory file found at %s; starting fresh.", self.file_path)
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                logger.info("Loaded %d prior turns from memory.", len(self.history))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load memory file (%s); starting fresh.", exc)
            self.history = []

    def add_turn(self, user: str, assistant: str) -> None:
        """Record one exchange (user message + assistant reply)."""
        self.history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": user,
                "assistant": assistant,
            }
        )
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages :]

    def recent(self, n: int = 10) -> List[Dict[str, str]]:
        """Return the last `n` conversational turns."""
        return self.history[-n:]

    def clear(self) -> None:
        """Wipe conversation history (in memory only, until save() is called)."""
        self.history = []

    def save(self) -> None:
        """Persist the current history to disk as JSON."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"history": self.history}, f, indent=2)
            logger.info("Saved %d turns to %s.", len(self.history), self.file_path)
        except OSError as exc:
            logger.error("Failed to save memory: %s", exc)
