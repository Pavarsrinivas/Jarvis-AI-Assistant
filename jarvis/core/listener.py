"""
listener.py
-----------
Handles wake-word detection and speech-to-text transcription using the
`speech_recognition` library and the system microphone.

Flow:
  1. Continuously listen to the microphone for short bursts of audio.
  2. Transcribe each burst and check whether it contains the wake word.
  3. Once the wake word is heard, listen again for the actual command
     and pass the transcribed text to the `on_command` callback.

This module intentionally isolates all microphone / STT dependencies so
the rest of the app never has to know which speech engine is in use.
"""

import logging
from typing import Callable, Optional

logger = logging.getLogger("jarvis.core.listener")

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None
    logger.warning(
        "speech_recognition is not installed. Run "
        "'pip install SpeechRecognition pyaudio' to enable voice input."
    )


class Listener:
    """Wraps microphone capture, wake-word detection, and STT transcription."""

    def __init__(
        self,
        wake_word: str,
        on_command: Callable[[str], None],
        listen_timeout: int = 5,
        phrase_time_limit: int = 10,
        ambient_noise_adjust: int = 1,
    ):
        self.wake_word = wake_word.lower()
        self.on_command = on_command
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit
        self.ambient_noise_adjust = ambient_noise_adjust
        
        self._recognizer = None
        self._microphone = None
        if sr:
            try:
                self._recognizer = sr.Recognizer()
                self._microphone = sr.Microphone()
            except (AttributeError, OSError) as exc:
                logger.warning("Microphone unavailable (%s). Using text mode.", exc)
                self._recognizer = None
                self._microphone = None

       
    def _transcribe_once(self) -> Optional[str]:
        """Capture a single utterance from the microphone and transcribe it."""
        if not self._recognizer or not self._microphone:
            return None

        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(
                source, duration=self.ambient_noise_adjust
            )
            try:
                audio = self._recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )
            except sr.WaitTimeoutError:
                return None

        try:
            return self._recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            logger.debug("Audio was not understood.")
            return None
        except sr.RequestError as exc:
            logger.error("STT service error: %s", exc)
            return None

    def listen_forever(self) -> None:
        """
        Main loop: listen for the wake word, then listen for and dispatch
        the follow-up command. Blocks until interrupted (Ctrl+C).
        """
        if not self._recognizer or not self._microphone:
            logger.error(
                "Microphone/STT backend unavailable. "
                "Falling back to text input mode."
            )
            self._text_fallback_loop()
            return

        logger.info("Listening for wake word '%s'...", self.wake_word)
        while True:
            heard = self._transcribe_once()
            if not heard:
                continue

            if self.wake_word in heard.lower():
                logger.info("Wake word detected.")
                command = self._transcribe_once()
                if command:
                    self.on_command(command)
            else:
                logger.debug("Ignored (no wake word): %s", heard)

    def _text_fallback_loop(self) -> None:
        """Keyboard-driven fallback for environments without a microphone."""
        print(f"[Text mode] Type your commands (say '{self.wake_word}' not required).")
        while True:
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                raise KeyboardInterrupt
            if text:
                self.on_command(text)
