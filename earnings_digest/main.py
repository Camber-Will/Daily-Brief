"""
main.py

Orchestrator for the Weekly Earnings Digest email.
Runs every Monday at 8am ET via GitHub Actions.

To run locally: python -m earnings_digest.main
"""

import base64
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from googleapiclient.discovery import build

from daily_brief.calendar_client import get_google_credentials
from earnings_digest.tickers import EARNINGS_TICKERS
from earnings_digest.earnings_fetcher import fetch_recent_earnings, fetch_upcoming_earnings
from earnings_digest.synthesizer import synthesize_earnings_report
from earnings_digest.email_builder import build_earnings_html


def send_earnings_email(html_content: str, report_count: int) -> None:
    recipient = os.environ.get("EARNINGS_RECIPIENT_EMAIL", "")
    if not recipient:
        raise ValueError(
            "EARNINGS_RECIPIENT_EMAIL environment variable is not set. "
            "Add it to your .env file or GitHub secrets."
        )

    if report_count == 0:
        subject = "📊 Earnings Digest — Nothing new this week"
    elif report_count == 1:
        subject = "📊 Earnings Digest — 1 report this week"
    else:
        subject = f"📊 Earnings Digest — {report_count} reports this week"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = os.environ.get("GMAIL_SENDER", recipient)
    msg["To"] = recipient

    plain = (
        f"{report_count} earnings report(s) from your portfolio this week.\n\n"
        "Open this email in an HTML-capable client to see the full digest."
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

    missing = [v for v in ["ANTHROPIC_API_KEY", "EARNINGS_RECIPIENT_EMAIL"] if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    has_cloud_creds = os.environ.get("GOOGLE_REFRESH_TOKEN") and os.environ.get("GOOGLE_CREDENTIALS")
    if not has_cloud_creds and not os.path.exists("token.json"):
        print("ERROR: No Google credentials found. Run 'python scripts/generate_token.py' first.")
        sys.exit(1)

    print("=" * 55)
    print("Weekly Earnings Digest — Starting")
    print("=" * 55)

    tickers = list(EARNINGS_TICKERS.keys())
    company_sections = []

    print(f"\nScanning {len(tickers)} tickers for earnings in the past 7 days...\n")

    for ticker, company in EARNINGS_TICKERS.items():
        print(f"  [{ticker}] {company}...", end=" ", flush=True)
        raw = fetch_recent_earnings(ticker, company)
        if raw is None:
            print("no report found")
            continue
        print(f"found! ({raw.get('quarter', '')})")
        section_html = synthesize_earnings_report(raw)
        company_sections.append(section_html)

    print(f"\nFound {len(company_sections)} report(s) this week.")

    print("\nChecking upcoming earnings for next week...")
    upcoming = fetch_upcoming_earnings(EARNINGS_TICKERS)
    if upcoming:
        names = ", ".join(f"{u['ticker']} ({u.get('expected_date_str', u.get('expected_date', ''))})" for u in upcoming)
        print(f"  Reporting next week: {names}")
    else:
        print("  No portfolio companies confirmed for next week.")

    print("\nBuilding and sending email...")
    html = build_earnings_html(company_sections, tickers, upcoming)
    send_earnings_email(html, len(company_sections))

    print("\nDone!")


if __name__ == "__main__":
    run()
