# JARVIS

A modular, voice-first AI assistant for the desktop. JARVIS listens for a
wake word, transcribes your speech, routes the command to the right
skill (or a general-purpose LLM chatbot as a fallback), and speaks the
response back to you — with conversation memory that persists across
sessions.

---

## Features

- **Wake-word listening** — always-on microphone loop that activates on a
  configurable wake word (default: "jarvis").
- **Speech-to-text & text-to-speech** — voice in, voice out, with an
  automatic text-input fallback if no microphone is available.
- **LLM-backed conversation** — general questions are answered by an
  OpenAI chat model, with recent conversation history included as context.
- **Skills** — deterministic handlers for common tasks:
  - *System control*: open applications, take screenshots, adjust volume,
    set reminders.
  - *Web search*: current weather, news headlines, Wikipedia summaries.
  - *File management*: find files, open files, auto-organize a folder
    (e.g. Downloads) into type-based subfolders.
- **Persistent memory** — conversation history is saved to
  `data/memory.json` and reloaded on the next run.

---

## Project Structure

```
NAYAK/
├── main.py                        # Entry point — starts JARVIS
├── config.py                      # API keys, settings, constants
├── requirements.txt               # All Python dependencies
├── .env.example                   # Template for your local .env file
├── README.md                      # This file
│
├── jarvis/
│   ├── core/
│   │   ├── listener.py            # Wake word detection + speech-to-text
│   │   ├── speaker.py             # Text-to-speech engine
│   │   ├── router.py              # Routes commands to correct module
│   │   └── memory.py              # Conversation history + context memory
│   │
│   ├── ai/
│   │   └── chatbot.py             # OpenAI GPT integration
│   │
│   ├── skills/
│   │   ├── system_control.py      # Open apps, screenshots, volume, reminders
│   │   ├── web_search.py          # Weather, news, Wikipedia lookups
│   │   └── file_manager.py        # File search, organize, open
│   │
│   └── utils/
│       └── helpers.py             # Shared utility functions
│
└── data/
    └── memory.json                # Persistent conversation memory store
```

---

## How It Works

```
 Microphone
     │
     ▼
 Listener  ──(wake word heard)──►  Listener  ──(command transcribed)──►  Router
 (listener.py)                                                              │
                                                                              │ pattern match?
                                              ┌───────────────────────────────┤
                                              ▼                               ▼
                                     Skills (system_control,          Chatbot (ai/chatbot.py)
                                     web_search, file_manager)         + Memory context
                                              │                               │
                                              └───────────────┬───────────────┘
                                                              ▼
                                                          Memory.add_turn()
                                                              │
                                                              ▼
                                                       Speaker.say(reply)
```

1. **`Listener`** captures microphone audio, checks for the wake word, then
   transcribes the next utterance as a command.
2. **`Router`** matches the command text against a set of regex patterns.
   If a skill matches, that skill's handler runs. Otherwise, the command is
   forwarded to the **`Chatbot`**.
3. **`Memory`** records every exchange and supplies recent history to the
   chatbot for context; it's saved to disk on shutdown.
4. **`Speaker`** converts the final reply to speech (and prints it to the
   console as a transcript either way).

---

## Setup

### 1. Prerequisites

- Python 3.9+
- A working microphone and speakers (optional — JARVIS falls back to
  keyboard/console mode if unavailable)
- An [OpenAI API key](https://platform.openai.com/api-keys) for the
  conversational fallback

### 2. Install dependencies

```bash
cd NAYAK
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> **Note:** `PyAudio` sometimes needs a system dependency first:
> - macOS: `brew install portaudio`
> - Linux: `sudo apt-get install portaudio19-dev python3-pyaudio`
> - Windows: usually installs via pip directly.

### 3. Configure API keys

Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-...
OPENWEATHER_API_KEY=...   # optional, enables the weather skill
NEWSAPI_API_KEY=...       # optional, enables the news skill
```

### 4. Run JARVIS

```bash
python main.py
```

Say **"Jarvis"** to wake it up, then speak your command. If no microphone
is detected, JARVIS automatically switches to a text-input prompt in the
terminal.

---

## Example Commands

| You say                                  | What happens                                   |
|-------------------------------------------|-------------------------------------------------|
| "Jarvis, open Spotify"                    | Launches the Spotify application                |
| "Jarvis, take a screenshot"               | Saves a PNG to `data/screenshots/`               |
| "Jarvis, volume up"                       | Raises system volume                             |
| "Jarvis, remind me to call mom"           | Acknowledges and notes a reminder                |
| "Jarvis, what's the weather in Tokyo?"    | Fetches current conditions via OpenWeather       |
| "Jarvis, what's the news?"                | Reads back top headlines via NewsAPI             |
| "Jarvis, who is Ada Lovelace?"             | Returns a short Wikipedia summary                |
| "Jarvis, find file resume.pdf"            | Searches your home directory for matching files  |
| "Jarvis, organize my downloads"           | Sorts Downloads into Documents/Images/etc.       |
| "Jarvis, tell me a joke" / anything else  | Falls back to the OpenAI chatbot                 |
| "Jarvis, exit" / "quit" / "goodbye"       | Shuts down and saves memory                      |

---

## Configuration Reference (`config.py`)

All settings can be overridden via environment variables (see
`.env.example`). Key options:

| Variable                    | Default        | Purpose                                  |
|------------------------------|----------------|-------------------------------------------|
| `JARVIS_WAKE_WORD`            | `jarvis`       | Word that activates command listening     |
| `JARVIS_MODEL`                | `gpt-4o-mini`  | OpenAI model for the chatbot fallback     |
| `JARVIS_TEMPERATURE`          | `0.6`          | Chatbot response creativity               |
| `JARVIS_TTS_RATE`             | `175`          | Speech rate (words/min) for TTS           |
| `JARVIS_DEFAULT_CITY`         | `London`       | Default city for weather lookups          |
| `JARVIS_DEFAULT_NEWS_COUNTRY` | `us`           | Default country code for news headlines   |
| `JARVIS_LOG_LEVEL`            | `INFO`         | Logging verbosity                         |

---

## Extending JARVIS

**Add a new skill:**
1. Create a function in the relevant file under `jarvis/skills/` (or a
   new file for a new skill category), returning a plain-text reply.
2. Register a trigger pattern + handler in `Router.routes` inside
   `jarvis/core/router.py`.

**Swap the STT/TTS backend:**
`listener.py` and `speaker.py` isolate all speech-engine-specific code,
so you can substitute e.g. Whisper or a cloud TTS provider by editing
only those two files — the rest of the app is unaffected.

**Change the LLM provider:**
`jarvis/ai/chatbot.py` wraps a single `ask(text) -> str` method. Swap the
OpenAI client for another provider's SDK without touching the router.

---

## Known Limitations

- Volume control and app launching use best-effort, OS-specific commands
  and may need adjustment for your particular OS/distro.
- The router uses simple regex matching rather than true intent
  classification — overlapping phrasing may route unpredictably.
- Reminders are in-memory only (no persistence or actual OS notifications)
  unless you extend `system_control.set_reminder`.

---

## License

MIT — use, modify, and extend freely.
