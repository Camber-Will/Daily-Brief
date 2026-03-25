"""
calendar_client.py

Fetches tomorrow's meetings from Google Calendar.
Think of this as the part that reads your calendar and says
"here's what's on tomorrow's schedule."
"""

import json
import os
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# The permissions (scopes) we need from Google
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_google_credentials() -> Credentials:
    """
    Build Google API credentials from environment variables.

    When running locally: reads from token.json (created by generate_token.py)
    When running in GitHub Actions: reconstructs from GOOGLE_CREDENTIALS + GOOGLE_REFRESH_TOKEN secrets
    """
    # --- Option A: GitHub Actions (cloud) ---
    # Uses the secrets stored in your GitHub repository
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")
    creds_json_str = os.environ.get("GOOGLE_CREDENTIALS")

    if refresh_token and creds_json_str:
        creds_data = json.loads(creds_json_str)
        # Handle both "installed" (desktop) and "web" credential types
        app_creds = creds_data.get("installed") or creds_data.get("web")
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=app_creds["client_id"],
            client_secret=app_creds["client_secret"],
            scopes=SCOPES,
        )
        # Refresh to get a valid access token
        creds.refresh(Request())
        return creds

    # --- Option B: Local development ---
    # Uses token.json created by running: python scripts/generate_token.py
    token_path = "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return creds

    raise RuntimeError(
        "No Google credentials found.\n"
        "For local use: run 'python scripts/generate_token.py' first.\n"
        "For GitHub Actions: add GOOGLE_CREDENTIALS and GOOGLE_REFRESH_TOKEN secrets."
    )


def get_tomorrows_meetings() -> list[dict]:
    """
    Returns a list of meetings scheduled for tomorrow.

    Each meeting is a dictionary with:
    - title: the meeting name
    - start_time: human-readable start time (e.g., "9:00 AM")
    - end_time: human-readable end time
    - attendees: list of email addresses
    - description: meeting description or agenda (if any)
    - location: video link or room (if any)
    """
    creds = get_google_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Calculate tomorrow's date range (midnight to midnight, local timezone)
    local_tz = timezone(timedelta(hours=-4))  # Eastern Time (EDT); change for your timezone
    now = datetime.now(local_tz)
    tomorrow_start = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    tomorrow_end = tomorrow_start + timedelta(days=1)

    # Fetch events from your primary calendar
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=tomorrow_start.isoformat(),
            timeMax=tomorrow_end.isoformat(),
            singleEvents=True,  # expand recurring events
            orderBy="startTime",
        )
        .execute()
    )

    raw_events = events_result.get("items", [])
    meetings = []

    for event in raw_events:
        # Skip all-day events (they have "date" instead of "dateTime")
        if "dateTime" not in event.get("start", {}):
            continue

        start_dt = datetime.fromisoformat(event["start"]["dateTime"])
        end_dt = datetime.fromisoformat(event["end"]["dateTime"])

        # Collect attendee emails (excluding your own)
        attendees = []
        my_email = os.environ.get("BRIEF_RECIPIENT_EMAIL", "").lower()
        for person in event.get("attendees", []):
            email = person.get("email", "").lower()
            if email and email != my_email:
                attendees.append(email)

        meetings.append(
            {
                "title": event.get("summary", "Untitled Meeting"),
                "start_time": start_dt.strftime("%-I:%M %p"),
                "end_time": end_dt.strftime("%-I:%M %p"),
                "start_iso": start_dt.isoformat(),
                "attendees": attendees,
                "description": event.get("description", ""),
                "location": event.get("location", ""),
            }
        )

    print(f"Found {len(meetings)} meetings for tomorrow.")
    return meetings
