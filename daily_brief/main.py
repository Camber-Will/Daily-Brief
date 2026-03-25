"""
main.py

The orchestrator — this is the file that runs everything.
Think of it like a conductor: it tells each musician (module) when to play.

Flow:
1. Load secrets from .env (local) or environment variables (GitHub Actions)
2. Fetch tomorrow's meetings from Google Calendar
3. For each meeting: get email context from Gmail + notes from Granola
4. Ask Claude AI to synthesize a brief for each meeting
5. Send the finished brief to your Gmail inbox

To run locally: python -m daily_brief.main
"""

import os
import sys
from dotenv import load_dotenv

from daily_brief.calendar_client import get_tomorrows_meetings
from daily_brief.gmail_client import get_email_context_for_meeting
from daily_brief.granola_client import get_granola_context_for_meeting
from daily_brief.ai_synthesizer import build_full_brief
from daily_brief.brief_sender import send_brief_via_gmail


def run():
    """Main entry point — runs the full daily brief pipeline."""

    # Step 0: Load secrets from .env file (only needed when running locally)
    # In GitHub Actions, these come from repository secrets automatically
    load_dotenv()

    # Verify required environment variables are present
    required_vars = ["ANTHROPIC_API_KEY", "BRIEF_RECIPIENT_EMAIL"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    # Also need at least one Google credential method
    has_cloud_creds = os.environ.get("GOOGLE_REFRESH_TOKEN") and os.environ.get("GOOGLE_CREDENTIALS")
    has_local_creds = os.path.exists("token.json")
    if not has_cloud_creds and not has_local_creds:
        print("ERROR: No Google credentials found.")
        print("Run 'python scripts/generate_token.py' to set up Google access.")
        sys.exit(1)

    print("=" * 50)
    print("Daily Meeting Brief — Starting")
    print("=" * 50)

    # Step 1: Get tomorrow's meetings from Google Calendar
    print("\n[1/4] Fetching tomorrow's meetings from Google Calendar...")
    meetings = get_tomorrows_meetings()

    if not meetings:
        print("No meetings found for tomorrow. Sending an all-clear brief.")
        # Still send an email so you know the system is working
        html = build_full_brief([])
        send_brief_via_gmail(html)
        print("\nDone! Sent all-clear brief.")
        return

    # Step 2: For each meeting, gather context
    print(f"\n[2/4] Gathering context for {len(meetings)} meeting(s)...")
    meetings_with_context = []

    for i, meeting in enumerate(meetings, 1):
        print(f"\n  Meeting {i}: {meeting['title']} at {meeting['start_time']}")

        # Get email threads from Gmail
        print("  → Searching Gmail...")
        email_context = get_email_context_for_meeting(meeting)

        # Get Granola notes (silently skipped if not available)
        print("  → Checking Granola notes...")
        granola_context = get_granola_context_for_meeting(meeting)
        if granola_context:
            print("  → Found relevant Granola notes!")

        meetings_with_context.append({
            "meeting": meeting,
            "email_context": email_context,
            "granola_context": granola_context,
        })

    # Step 3: Ask Claude AI to synthesize the brief
    print(f"\n[3/4] Synthesizing brief with Claude AI ({len(meetings)} meeting(s))...")
    html_brief = build_full_brief(meetings_with_context)

    # Optional: save a local copy for debugging
    if os.environ.get("SAVE_LOCAL_COPY", "").lower() == "true":
        with open("brief_output.html", "w") as f:
            f.write(html_brief)
        print("  Saved local copy to brief_output.html")

    # Step 4: Send the brief via Gmail
    print("\n[4/4] Sending brief via Gmail...")
    send_brief_via_gmail(html_brief)

    print("\n" + "=" * 50)
    print("Done! Your Daily Meeting Brief has been sent.")
    print("=" * 50)


if __name__ == "__main__":
    run()
