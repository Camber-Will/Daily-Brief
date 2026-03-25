"""
granola_client.py

Reads meeting notes from Granola (a meeting notes app).
Think of this as the part that checks your past meeting notes for context
before you walk into a meeting.

How Granola integration works:
- Granola saves notes to ~/Library/Application Support/Granola/notes/ on Mac
- You can also set GRANOLA_NOTES_DIR to any folder where you export notes
- This only works when running LOCALLY (Granola lives on your computer)
- When running in GitHub Actions (cloud), this is automatically skipped
"""

import os
import re
from pathlib import Path


def _find_granola_notes_dir() -> Path | None:
    """Find where Granola stores notes on this machine."""
    # Check environment variable first
    env_dir = os.environ.get("GRANOLA_NOTES_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.exists():
            return path

    # Try the default Mac location
    default_mac = Path.home() / "Library" / "Application Support" / "Granola" / "notes"
    if default_mac.exists():
        return default_mac

    # Try a local notes/ folder in the project
    local_notes = Path("notes")
    if local_notes.exists():
        return local_notes

    return None


def _read_note_file(file_path: Path) -> str:
    """Read a note file and return its text content."""
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _is_relevant(note_text: str, keywords: list[str]) -> bool:
    """Check if a note mentions any of the given keywords (case-insensitive)."""
    note_lower = note_text.lower()
    return any(kw.lower() in note_lower for kw in keywords if kw)


def get_granola_context_for_meeting(meeting: dict) -> str:
    """
    Search Granola notes for context relevant to this meeting.
    Returns a formatted string, or an empty string if nothing found.

    This function gracefully does nothing when:
    - Running in GitHub Actions (no Granola installed)
    - Granola notes folder doesn't exist
    - No relevant notes found
    """
    notes_dir = _find_granola_notes_dir()
    if not notes_dir:
        return ""  # Silently skip — Granola not available in this environment

    # Build keywords to search for: meeting title words + attendee names/companies
    keywords = []

    # Add words from meeting title (skip short/common words)
    stop_words = {"a", "an", "the", "and", "or", "with", "for", "of", "in", "at", "on"}
    title_words = [w for w in re.split(r"\W+", meeting["title"]) if len(w) > 2 and w.lower() not in stop_words]
    keywords.extend(title_words)

    # Add attendee company names
    for email in meeting["attendees"]:
        domain = email.split("@")[-1] if "@" in email else ""
        generic = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
        if domain and domain not in generic:
            company = domain.split(".")[0]
            keywords.append(company)

    if not keywords:
        return ""

    # Search all note files (markdown, txt, json)
    relevant_notes = []
    note_files = list(notes_dir.glob("*.md")) + list(notes_dir.glob("*.txt"))

    for note_path in sorted(note_files, key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
        content = _read_note_file(note_path)
        if _is_relevant(content, keywords):
            # Extract a preview (first 500 chars)
            preview = content[:500].strip()
            relevant_notes.append(f"[Note: {note_path.stem}]\n{preview}")

        if len(relevant_notes) >= 3:  # Limit to 3 most recent relevant notes
            break

    if not relevant_notes:
        return ""

    return "GRANOLA MEETING NOTES:\n" + "\n\n".join(relevant_notes)
