"""
router.py
---------
Routes a transcribed command string to the correct handler: a specific
skill (system control, web search, file management) if the intent is
recognized, or the general-purpose chatbot as a fallback.

Routing here is deliberately simple and keyword-based so the project
has no hard external NLU dependency. It can be swapped out for a more
sophisticated intent classifier later without changing the public
`Router.route()` interface.
"""

import logging
import re
from typing import Callable, Dict, List, Tuple

from jarvis.ai.chatbot import Chatbot
from jarvis.skills import system_control, web_search, file_manager

logger = logging.getLogger("jarvis.core.router")


class Router:
    """Maps user commands to skill handlers, with the chatbot as a fallback."""

    def __init__(self, memory, speaker):
        self.memory = memory
        self.speaker = speaker
        self.chatbot = Chatbot(memory=memory)

        # Each entry: (list of trigger regex patterns, handler function)
        # Handlers receive the raw command text and must return a string reply.
        self.routes: List[Tuple[List[re.Pattern], Callable[[str], str]]] = [
            (
                [re.compile(r"\bopen\s+(.+)", re.I)],
                self._route_open_app,
            ),
            (
                [re.compile(r"\b(screenshot|take a screenshot)\b", re.I)],
                lambda text: system_control.take_screenshot(),
            ),
            (
                [re.compile(r"\bvolume\s+(up|down|mute|\d+)\b", re.I)],
                self._route_volume,
            ),
            (
                [re.compile(r"\bremind me (to|about) (.+)", re.I)],
                self._route_reminder,
            ),
            (
                [re.compile(r"\b(weather)\b", re.I)],
                self._route_weather,
            ),
            (
                [re.compile(r"\b(news|headlines)\b", re.I)],
                lambda text: web_search.get_news(),
            ),
            (
                [re.compile(r"\bwikipedia\b|\bwho is\b|\bwhat is\b", re.I)],
                self._route_wikipedia,
            ),
            (
                [re.compile(r"\bfind file\b|\bsearch for file\b", re.I)],
                self._route_find_file,
            ),
            (
                [re.compile(r"\borganize\s+(my\s+)?(downloads|files)\b", re.I)],
                lambda text: file_manager.organize_downloads(),
            ),
        ]

    def route(self, text: str) -> str:
        """
        Determine the appropriate handler for `text` and return its reply.
        Falls back to the LLM chatbot if no skill pattern matches.
        """
        for patterns, handler in self.routes:
            for pattern in patterns:
                if pattern.search(text):
                    try:
                        reply = handler(text)
                    except Exception as exc:
                        logger.exception("Skill handler failed: %s", exc)
                        reply = "Sorry, I ran into an error handling that request."
                    self.memory.add_turn(user=text, assistant=reply)
                    return reply

        # No skill matched -> hand off to the general chatbot.
        reply = self.chatbot.ask(text)
        self.memory.add_turn(user=text, assistant=reply)
        return reply

    # ------------------------------------------------------------------
    # Individual route handlers
    # ------------------------------------------------------------------
    @staticmethod
    def _route_open_app(text: str) -> str:
        match = re.search(r"\bopen\s+(.+)", text, re.I)
        target = match.group(1).strip() if match else ""
        return system_control.open_application(target)

    @staticmethod
    def _route_volume(text: str) -> str:
        match = re.search(r"\bvolume\s+(up|down|mute|\d+)\b", text, re.I)
        action = match.group(1).lower() if match else "up"
        return system_control.set_volume(action)

    @staticmethod
    def _route_reminder(text: str) -> str:
        match = re.search(r"\bremind me (?:to|about) (.+)", text, re.I)
        content = match.group(1).strip() if match else text
        return system_control.set_reminder(content)

    @staticmethod
    def _route_weather(text: str) -> str:
        match = re.search(r"weather\s+(?:in|for)\s+([a-zA-Z\s]+)", text, re.I)
        city = match.group(1).strip() if match else None
        return web_search.get_weather(city)

    @staticmethod
    def _route_wikipedia(text: str) -> str:
        query = re.sub(r"\b(what is|who is|wikipedia)\b", "", text, flags=re.I).strip()
        return web_search.search_wikipedia(query or text)

    @staticmethod
    def _route_find_file(text: str) -> str:
        match = re.search(r"(?:find file|search for file)\s+(.+)", text, re.I)
        filename = match.group(1).strip() if match else ""
        return file_manager.find_file(filename)
