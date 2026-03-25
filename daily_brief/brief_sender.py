"""
brief_sender.py

Sends the finished Daily Brief to Will's Gmail inbox.
Think of this as the part that puts the finished report in your mailbox.

Delivery method: Gmail (using the same Google credentials already set up)
"""

import base64
import os
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from daily_brief.calendar_client import get_google_credentials


def send_brief_via_gmail(html_content: str) -> bool:
    """
    Send the HTML brief as an email via Gmail API.

    Returns True if sent successfully, False otherwise.
    """
    recipient = os.environ.get("BRIEF_RECIPIENT_EMAIL", "")
    if not recipient:
        raise ValueError(
            "BRIEF_RECIPIENT_EMAIL environment variable is not set. "
            "Add it to your .env file or GitHub secrets."
        )

    # Build the email subject
    et_tz = timezone(timedelta(hours=-4))
    tomorrow = (datetime.now(et_tz) + timedelta(days=1)).strftime("%A, %b %-d")
    subject = f"📅 Daily Meeting Brief — {tomorrow}"

    # Create a multipart email (plain text fallback + HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = recipient  # Send from your own address (Gmail API uses authenticated user)
    msg["To"] = recipient

    # Plain text fallback (for email clients that don't render HTML)
    plain_text = "Your Daily Meeting Brief is ready. Please open this email in an HTML-capable client to view it."
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Encode the email for Gmail API (it expects base64url encoding)
    raw_email = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    # Send via Gmail API
    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    result = service.users().messages().send(
        userId="me",
        body={"raw": raw_email},
    ).execute()

    print(f"Brief sent successfully! Gmail Message ID: {result.get('id')}")
    print(f"Delivered to: {recipient}")
    return True
