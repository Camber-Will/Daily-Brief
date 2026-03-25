"""
gmail_client.py

Searches Gmail for recent email threads related to each meeting attendee.
Think of this as the part that digs through your inbox and surfaces
relevant conversations you've had with the people you're meeting tomorrow.
"""

import base64
import re
from googleapiclient.discovery import build
from daily_brief.calendar_client import get_google_credentials


def _decode_message_body(payload: dict) -> str:
    """Extract plain text from a Gmail message payload."""
    body = ""

    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    elif payload.get("mimeType", "").startswith("multipart/"):
        for part in payload.get("parts", []):
            body += _decode_message_body(part)

    # Clean up: remove excessive whitespace
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body[:2000]  # Limit to 2000 chars per message to control costs


def get_threads_for_attendee(service, attendee_email: str, max_threads: int = 5) -> list[dict]:
    """
    Search Gmail for recent threads with a specific attendee.
    Returns a list of thread summaries.
    """
    # Search for emails from OR to this person in the last 30 days
    query = f"(from:{attendee_email} OR to:{attendee_email}) newer_than:30d"

    results = service.users().threads().list(
        userId="me",
        q=query,
        maxResults=max_threads,
    ).execute()

    threads = results.get("threads", [])
    summaries = []

    for thread in threads:
        thread_data = service.users().threads().get(
            userId="me",
            id=thread["id"],
            format="full",
        ).execute()

        messages = thread_data.get("messages", [])
        if not messages:
            continue

        # Get subject from first message headers
        first_msg = messages[0]
        headers = {h["name"]: h["value"] for h in first_msg.get("payload", {}).get("headers", [])}
        subject = headers.get("Subject", "(no subject)")

        # Get snippet from last message (most recent)
        last_msg = messages[-1]
        snippet = last_msg.get("snippet", "")

        # Get the body of the most recent message
        body = _decode_message_body(last_msg.get("payload", {}))

        summaries.append({
            "subject": subject,
            "message_count": len(messages),
            "snippet": snippet,
            "body_preview": body[:500],
        })

    return summaries


def get_threads_for_company(service, attendee_email: str, max_threads: int = 3) -> list[dict]:
    """
    Search Gmail for recent threads about the attendee's company.
    Useful for catching news or context not directly in a 1:1 thread.
    """
    # Extract company domain (e.g., "apple.com" → "apple")
    parts = attendee_email.split("@")
    if len(parts) < 2:
        return []

    domain = parts[1]
    # Skip common personal email domains
    generic_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
    if domain in generic_domains:
        return []

    company = domain.split(".")[0]
    query = f'"{company}" newer_than:30d -from:me'

    results = service.users().threads().list(
        userId="me",
        q=query,
        maxResults=max_threads,
    ).execute()

    threads = results.get("threads", [])
    summaries = []

    for thread in threads:
        thread_data = service.users().threads().get(
            userId="me",
            id=thread["id"],
            format="metadata",
            metadataHeaders=["Subject", "From"],
        ).execute()

        messages = thread_data.get("messages", [])
        if not messages:
            continue

        headers = {
            h["name"]: h["value"]
            for h in messages[0].get("payload", {}).get("headers", [])
        }
        subject = headers.get("Subject", "(no subject)")
        snippet = messages[-1].get("snippet", "")

        summaries.append({
            "subject": subject,
            "snippet": snippet,
            "body_preview": "",
        })

    return summaries


def get_email_context_for_meeting(meeting: dict) -> str:
    """
    Given a meeting dict (from calendar_client), return a formatted string
    of relevant email context for use in the AI synthesis prompt.
    """
    if not meeting["attendees"]:
        return "No external attendees found — internal meeting or personal event."

    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    context_parts = []

    for attendee_email in meeting["attendees"][:3]:  # Limit to 3 attendees to control API calls
        print(f"  Searching emails for: {attendee_email}")

        # Get direct threads with this person
        threads = get_threads_for_attendee(service, attendee_email)
        company_threads = get_threads_for_company(service, attendee_email)

        if threads or company_threads:
            context_parts.append(f"\n--- Emails with {attendee_email} ---")

        for t in threads:
            context_parts.append(
                f"Subject: {t['subject']}\n"
                f"({t['message_count']} messages) {t['snippet']}\n"
                f"{t['body_preview']}"
            )

        if company_threads:
            context_parts.append(f"\n--- Company context for {attendee_email.split('@')[1]} ---")
            for t in company_threads:
                context_parts.append(f"Subject: {t['subject']}\n{t['snippet']}")

    if not context_parts:
        return "No recent email threads found with these attendees."

    return "\n\n".join(context_parts)
