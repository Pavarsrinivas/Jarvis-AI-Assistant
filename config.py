"""
config.py
---------
Central configuration for JARVIS: API keys, tunable settings, and
constants used across the application.

Secrets should NOT be hard-coded here in a real deployment. Instead,
set them as environment variables (e.g. in a .env file loaded via
python-dotenv) and this module will pick them up automatically.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; fall back to real environment variables.
    pass

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
ASSISTANT_NAME = "JARVIS"
WAKE_WORD = os.getenv("JARVIS_WAKE_WORD", "jarvis")

# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY", "")

# ---------------------------------------------------------------------------
# Chatbot / LLM settings
# ---------------------------------------------------------------------------
OPENAI_MODEL = os.getenv("JARVIS_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("JARVIS_TEMPERATURE", "0.6"))
OPENAI_MAX_TOKENS = int(os.getenv("JARVIS_MAX_TOKENS", "512"))
SYSTEM_PROMPT = (
    "You are JARVIS, a concise, helpful voice assistant. "
    "Keep spoken replies short and natural, ideally under 3 sentences "
    "unless the user asks for detail."
)

# ---------------------------------------------------------------------------
# Speech-to-text / wake word settings
# ---------------------------------------------------------------------------
STT_ENGINE = os.getenv("JARVIS_STT_ENGINE", "google")  # google | whisper
LISTEN_TIMEOUT_SECONDS = 5
PHRASE_TIME_LIMIT_SECONDS = 10
AMBIENT_NOISE_ADJUST_SECONDS = 1

# ---------------------------------------------------------------------------
# Text-to-speech settings
# ---------------------------------------------------------------------------
TTS_ENGINE = os.getenv("JARVIS_TTS_ENGINE", "pyttsx3")  # pyttsx3 | none
TTS_RATE = int(os.getenv("JARVIS_TTS_RATE", "175"))
TTS_VOLUME = float(os.getenv("JARVIS_TTS_VOLUME", "1.0"))
TTS_VOICE_INDEX = int(os.getenv("JARVIS_TTS_VOICE_INDEX", "0"))

# ---------------------------------------------------------------------------
# Memory settings
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE_PATH = os.path.join(BASE_DIR, "data", "memory.json")
MAX_MEMORY_MESSAGES = 50  # trim conversation history beyond this many turns

# ---------------------------------------------------------------------------
# Skills settings
# ---------------------------------------------------------------------------
SCREENSHOT_DIR = os.path.join(BASE_DIR, "data", "screenshots")
DEFAULT_WEATHER_CITY = os.getenv("JARVIS_DEFAULT_CITY", "London")
DEFAULT_NEWS_COUNTRY = os.getenv("JARVIS_DEFAULT_NEWS_COUNTRY", "us")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("JARVIS_LOG_LEVEL", "INFO")
