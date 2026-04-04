"""
tracker.py

Tracks progress toward the June 21, 2026 goal.
Returns days elapsed, days remaining, and percentage complete.
"""

from datetime import date


GOAL_START = date(2026, 4, 3)
GOAL_END = date(2026, 6, 21)
TOTAL_DAYS = (GOAL_END - GOAL_START).days  # 79


def get_progress() -> dict:
    """Return progress stats as of today."""
    today = date.today()

    days_elapsed = max(0, (today - GOAL_START).days)
    days_remaining = max(0, (GOAL_END - today).days)
    pct_complete = min(100.0, round(days_elapsed / TOTAL_DAYS * 100, 1))

    return {
        "today": today,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "pct_complete": pct_complete,
        "total_days": TOTAL_DAYS,
        "goal_end": GOAL_END,
    }
