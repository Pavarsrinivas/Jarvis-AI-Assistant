"""
web_search.py
-------------
Skill module for internet-backed lookups: current weather (OpenWeather),
top news headlines (NewsAPI), and general knowledge summaries
(Wikipedia).

Each function degrades gracefully with a helpful message if the
relevant API key is missing or the request fails, so JARVIS never
crashes on a bad network call.
"""

import logging

import requests

from config import (
    OPENWEATHER_API_KEY,
    NEWSAPI_API_KEY,
    DEFAULT_WEATHER_CITY,
    DEFAULT_NEWS_COUNTRY,
)

logger = logging.getLogger("jarvis.skills.web_search")

try:
    import wikipedia
except ImportError:  # pragma: no cover - optional dependency
    wikipedia = None
    logger.warning(
        "wikipedia package is not installed. Run 'pip install wikipedia' "
        "to enable knowledge lookups."
    )


def get_weather(city: str = None) -> str:
    """Fetch current weather for `city` (or the configured default city)."""
    city = city or DEFAULT_WEATHER_CITY

    if not OPENWEATHER_API_KEY:
        return "Weather lookups need an OPENWEATHER_API_KEY set in your environment."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        return (
            f"It's currently {temp:.0f}°C in {city}, feels like {feels_like:.0f}°C, "
            f"with {description}."
        )
    except requests.exceptions.HTTPError:
        return f"I couldn't find weather data for '{city}'. Could you check the city name?"
    except requests.exceptions.RequestException as exc:
        logger.error("Weather request failed: %s", exc)
        return "I'm having trouble reaching the weather service right now."


def get_news(country: str = None, page_size: int = 5) -> str:
    """Fetch top headlines for `country` (or the configured default)."""
    country = country or DEFAULT_NEWS_COUNTRY

    if not NEWSAPI_API_KEY:
        return "News lookups need a NEWSAPI_API_KEY set in your environment."

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": country,
                "apiKey": NEWSAPI_API_KEY,
                "pageSize": page_size,
            },
            timeout=8,
        )
        response.raise_for_status()
        articles = response.json().get("articles", [])

        if not articles:
            return "I couldn't find any headlines right now."

        headlines = [article["title"] for article in articles[:page_size]]
        return "Here are the top headlines: " + "; ".join(headlines)
    except requests.exceptions.RequestException as exc:
        logger.error("News request failed: %s", exc)
        return "I'm having trouble reaching the news service right now."


def search_wikipedia(query: str, sentences: int = 2) -> str:
    """Return a short Wikipedia summary for `query`."""
    if not wikipedia:
        return "Knowledge lookups need the 'wikipedia' package installed."

    if not query:
        return "What would you like me to look up?"

    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as exc:
        options = ", ".join(exc.options[:5])
        return f"That's a bit ambiguous. Did you mean: {options}?"
    except wikipedia.exceptions.PageError:
        return f"I couldn't find a Wikipedia page for '{query}'."
    except Exception as exc:
        logger.error("Wikipedia lookup failed: %s", exc)
        return "I'm having trouble searching Wikipedia right now."
