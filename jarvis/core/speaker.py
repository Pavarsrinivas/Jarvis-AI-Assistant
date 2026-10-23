"""
speaker.py
----------
Text-to-speech engine for JARVIS, built on `pyttsx3` (offline TTS).

Falls back to printing to stdout if pyttsx3 or a compatible TTS driver
is not available, so the rest of the application can always call
`Speaker.say(...)` without worrying about the environment.
"""

import logging

from config import TTS_RATE, TTS_VOLUME, TTS_VOICE_INDEX

logger = logging.getLogger("jarvis.core.speaker")

try:
    import pyttsx3
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None
    logger.warning(
        "pyttsx3 is not installed. Run 'pip install pyttsx3' to enable "
        "spoken output. Falling back to printed text."
    )


class Speaker:
    """Converts text responses into speech (or console output as a fallback)."""

    def __init__(self):
        self._engine = None
        if pyttsx3:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", TTS_RATE)
                self._engine.setProperty("volume", TTS_VOLUME)
                voices = self._engine.getProperty("voices")
                if voices:
                    index = min(TTS_VOICE_INDEX, len(voices) - 1)
                    self._engine.setProperty("voice", voices[index].id)
            except Exception as exc:  # pragma: no cover - platform dependent
                logger.error("Failed to initialize TTS engine: %s", exc)
                self._engine = None

    def say(self, text: str) -> None:
        """Speak the given text aloud, printing it regardless as a transcript."""
        print(f"JARVIS: {text}")
        if not self._engine or not text:
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as exc:  # pragma: no cover - platform dependent
            logger.error("TTS playback failed: %s", exc)
