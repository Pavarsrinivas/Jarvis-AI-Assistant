"""
main.py
--------
Entry point for JARVIS.

Starts the listener loop, which waits for the wake word, transcribes
speech, routes the resulting command through the Router, and speaks
back the response using the Speaker module.

Usage:
    python main.py

Environment:
    Requires a valid OpenAI API key set in config.py or as the
    OPENAI_API_KEY environment variable.
"""

import sys
import signal
import logging

from config import (
    WAKE_WORD,
    LOG_LEVEL,
    ASSISTANT_NAME,
)
from jarvis.core.listener import Listener
from jarvis.core.speaker import Speaker
from jarvis.core.router import Router
from jarvis.core.memory import Memory

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("jarvis.main")


class Jarvis:
    """Top-level orchestrator that wires together all JARVIS subsystems."""

    def __init__(self):
        self.memory = Memory()
        self.speaker = Speaker()
        self.router = Router(memory=self.memory, speaker=self.speaker)
        self.listener = Listener(wake_word=WAKE_WORD, on_command=self.handle_command)
        self._running = False

    def handle_command(self, text: str) -> None:
        """Callback invoked by the Listener whenever a command is heard."""
        logger.info("Heard command: %s", text)
        if not text:
            return

        if text.strip().lower() in ("exit", "quit", "stop", "shutdown", "goodbye"):
            self.speaker.say(f"Goodbye. {ASSISTANT_NAME} is shutting down.")
            self.stop()
            return

        response = self.router.route(text)
        if response:
            self.speaker.say(response)

    def start(self) -> None:
        """Start the main listening loop."""
        self._running = True
        self.speaker.say(f"{ASSISTANT_NAME} is online. Say '{WAKE_WORD}' to begin.")
        logger.info("%s started. Waiting for wake word '%s'.", ASSISTANT_NAME, WAKE_WORD)
        try:
            self.listener.listen_forever()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Gracefully stop JARVIS and persist memory to disk."""
        self._running = False
        self.memory.save()
        logger.info("%s stopped.", ASSISTANT_NAME)
        sys.exit(0)


def _handle_sigint(jarvis: Jarvis, signum, frame):
    jarvis.stop()


def main() -> None:
    jarvis = Jarvis()
    signal.signal(signal.SIGINT, lambda s, f: _handle_sigint(jarvis, s, f))
    jarvis.start()


if __name__ == "__main__":
    main()
