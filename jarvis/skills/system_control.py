"""
system_control.py
------------------
Skill module for controlling the local machine: launching applications,
taking screenshots, adjusting system volume, and setting simple
reminders.

Platform notes:
  - Application launching and volume control use OS-specific commands
    (macOS: `open` / `osascript`, Windows: `os.startfile` / `nircmd`
    or PowerShell, Linux: `xdg-open` / `amixer`). Only a best-effort
    cross-platform implementation is provided here; extend per-OS as
    needed for production use.
"""

import logging
import os
import platform
import subprocess
import threading
import time
from datetime import datetime

from config import SCREENSHOT_DIR

logger = logging.getLogger("jarvis.skills.system_control")

try:
    import pyautogui
except ImportError:  # pragma: no cover - optional dependency
    pyautogui = None
    logger.warning(
        "pyautogui is not installed. Run 'pip install pyautogui' to "
        "enable screenshots."
    )

_SYSTEM = platform.system()  # 'Windows', 'Darwin', or 'Linux'


def open_application(app_name: str) -> str:
    """Attempt to launch an application by name, in an OS-appropriate way."""
    if not app_name:
        return "I didn't catch which application to open."

    try:
        if _SYSTEM == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        elif _SYSTEM == "Windows":
            os.startfile(app_name)  # nosec - user-triggered, local app name
        else:  # Linux and others
            subprocess.Popen([app_name.lower()])
        return f"Opening {app_name}."
    except Exception as exc:
        logger.error("Failed to open '%s': %s", app_name, exc)
        return f"I couldn't open {app_name}. Is it installed?"


def take_screenshot() -> str:
    """Capture the current screen and save it to the screenshots directory."""
    if not pyautogui:
        return "Screenshot support isn't available — pyautogui is not installed."

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)

    try:
        image = pyautogui.screenshot()
        image.save(path)
        return f"Screenshot saved to {path}."
    except Exception as exc:
        logger.error("Screenshot failed: %s", exc)
        return "Sorry, I couldn't take a screenshot."


def set_volume(action: str) -> str:
    """Adjust system volume. `action` is 'up', 'down', 'mute', or a 0-100 number."""
    try:
        if _SYSTEM == "Darwin":
            if action == "mute":
                subprocess.run(["osascript", "-e", "set volume output muted true"])
            elif action.isdigit():
                subprocess.run(
                    ["osascript", "-e", f"set volume output volume {int(action)}"]
                )
            elif action == "up":
                subprocess.run(["osascript", "-e", "set volume output volume 80"])
            elif action == "down":
                subprocess.run(["osascript", "-e", "set volume output volume 20"])
        elif _SYSTEM == "Linux":
            if action == "mute":
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "mute"])
            elif action.isdigit():
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", f"{action}%"])
            elif action == "up":
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "10%+"])
            elif action == "down":
                subprocess.run(["amixer", "-D", "pulse", "set", "Master", "10%-"])
        else:
            logger.warning("Volume control not implemented for %s", _SYSTEM)
            return "Volume control isn't set up for this operating system yet."

        return f"Volume set to {action}."
    except Exception as exc:
        logger.error("Volume control failed: %s", exc)
        return "I couldn't change the volume."


def set_reminder(content: str, delay_seconds: int = 0) -> str:
    """
    Schedule a simple in-process reminder. For `delay_seconds` > 0, a
    background timer will print/log the reminder when it fires.
    For 0 (default), this just acknowledges the reminder was noted —
    wire this up to persistent storage or a calendar API for real use.
    """
    if not content:
        return "What would you like me to remind you about?"

    if delay_seconds > 0:
        def _fire():
            time.sleep(delay_seconds)
            logger.info("REMINDER: %s", content)
            print(f"\n🔔 Reminder: {content}\n")

        threading.Thread(target=_fire, daemon=True).start()
        return f"Okay, I'll remind you about '{content}' in {delay_seconds} seconds."

    return f"Got it — I noted a reminder: '{content}'."
