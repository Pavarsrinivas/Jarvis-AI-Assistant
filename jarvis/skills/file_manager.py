"""
file_manager.py
----------------
Skill module for local file operations: searching for files by name,
organizing a directory (e.g. Downloads) into type-based subfolders,
and opening files with the OS default application.
"""

import logging
import os
import platform
import shutil
import subprocess

logger = logging.getLogger("jarvis.skills.file_manager")

_SYSTEM = platform.system()

# Extension -> destination subfolder, used by organize_downloads().
_CATEGORY_MAP = {
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents", ".txt": "Documents",
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images", ".svg": "Images",
    ".mp4": "Videos", ".mov": "Videos", ".avi": "Videos", ".mkv": "Videos",
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".py": "Code", ".js": "Code", ".java": "Code", ".cpp": "Code", ".c": "Code", ".html": "Code",
    ".xlsx": "Spreadsheets", ".csv": "Spreadsheets", ".xls": "Spreadsheets",
    ".pptx": "Presentations", ".ppt": "Presentations",
}


def find_file(filename: str, search_root: str = None) -> str:
    """
    Search for a file by (partial) name starting from `search_root`
    (defaults to the user's home directory). Returns the first few matches.
    """
    if not filename:
        return "What file should I search for?"

    root = search_root or os.path.expanduser("~")
    matches = []

    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if filename.lower() in name.lower():
                matches.append(os.path.join(dirpath, name))
                if len(matches) >= 5:
                    break
        if len(matches) >= 5:
            break

    if not matches:
        return f"I couldn't find any file matching '{filename}'."

    listing = "; ".join(matches)
    return f"Found {len(matches)} match(es): {listing}"


def open_file(path: str) -> str:
    """Open a file with the OS default application."""
    if not path or not os.path.exists(path):
        return f"I can't find a file at '{path}'."

    try:
        if _SYSTEM == "Darwin":
            subprocess.run(["open", path])
        elif _SYSTEM == "Windows":
            os.startfile(path)  # nosec - user-provided local path
        else:
            subprocess.run(["xdg-open", path])
        return f"Opening {os.path.basename(path)}."
    except Exception as exc:
        logger.error("Failed to open file '%s': %s", path, exc)
        return f"I couldn't open {os.path.basename(path)}."


def organize_downloads(source_dir: str = None) -> str:
    """
    Sort files in `source_dir` (defaults to ~/Downloads) into
    type-based subfolders (Documents, Images, Videos, etc.).
    """
    source_dir = source_dir or os.path.join(os.path.expanduser("~"), "Downloads")

    if not os.path.isdir(source_dir):
        return f"I couldn't find the folder '{source_dir}'."

    moved_count = 0
    for entry in os.listdir(source_dir):
        full_path = os.path.join(source_dir, entry)
        if not os.path.isfile(full_path):
            continue

        _, ext = os.path.splitext(entry)
        category = _CATEGORY_MAP.get(ext.lower(), "Other")
        dest_dir = os.path.join(source_dir, category)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            shutil.move(full_path, os.path.join(dest_dir, entry))
            moved_count += 1
        except Exception as exc:
            logger.error("Failed to move '%s': %s", entry, exc)

    if moved_count == 0:
        return "There was nothing new to organize."
    return f"Organized {moved_count} file(s) in {source_dir} by type."
