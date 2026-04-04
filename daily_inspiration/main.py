"""
main.py

Orchestrator for the Daily Inspiration email.
Runs every morning at 8am ET via GitHub Actions.

To run locally: python -m daily_inspiration.main
"""

import base64
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from googleapiclient.discovery import build

from daily_brief.calendar_client import get_google_credentials
from daily_inspiration.tracker import get_progress
from daily_inspiration.quote_generator import generate_quote
from daily_inspiration.email_builder import build_inspiration_html


def send_inspiration_email(html_content: str, days_remaining: int) -> None:
    recipient = os.environ.get("INSPIRATION_RECIPIENT_EMAIL", "")
    if not recipient:
        raise ValueError(
            "INSPIRATION_RECIPIENT_EMAIL environment variable is not set. "
            "Add it to your .env file or GitHub secrets."
        )

    day_label = "day" if days_remaining == 1 else "days"
    if days_remaining == 0:
        subject = "🎉 You made it — June 21st is here!"
    else:
        subject = f"🌅 {days_remaining} {day_label} to go — Your morning fuel"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.environ.get("GMAIL_SENDER", recipient)
    msg["To"] = recipient

    plain = (
        f"{days_remaining} days remaining until June 21st.\n\n"
        "Open this email in an HTML-capable client to see your daily quote and progress tracker."
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    print(f"Sent! Gmail Message ID: {result.get('id')}")
    print(f"Delivered to: {recipient}")


def run():
    load_dotenv()

    missing = [v for v in ["ANTHROPIC_API_KEY", "INSPIRATION_RECIPIENT_EMAIL"] if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    has_cloud_creds = os.environ.get("GOOGLE_REFRESH_TOKEN") and os.environ.get("GOOGLE_CREDENTIALS")
    if not has_cloud_creds and not os.path.exists("token.json"):
        print("ERROR: No Google credentials found. Run 'python scripts/generate_token.py' first.")
        sys.exit(1)

    print("=" * 50)
    print("Daily Inspiration — Starting")
    print("=" * 50)

    print("\n[1/3] Calculating goal progress...")
    progress = get_progress()
    print(f"  Days remaining: {progress['days_remaining']} / {progress['total_days']}")
    print(f"  Progress: {progress['pct_complete']}% complete")

    print("\n[2/3] Generating today's quote with Claude...")
    quote = generate_quote(progress["days_remaining"], progress["pct_complete"])
    print(f"  Quote: {quote['quote'][:80]}...")

    print("\n[3/3] Building and sending email...")
    html = build_inspiration_html(progress, quote)
    send_inspiration_email(html, progress["days_remaining"])

    print("\nDone!")


if __name__ == "__main__":
    run()
