"""
ai_synthesizer.py

Uses Claude AI to synthesize meeting context into a clean, skimmable brief.
Think of this as the part that takes all the raw information (emails, notes)
and turns it into something you can actually read in 2 minutes.
"""

import os
import anthropic


# Initialize the Claude client
# The API key is read automatically from the ANTHROPIC_API_KEY environment variable
_client = None


def _get_client() -> anthropic.Anthropic:
    """Get (or create) the Anthropic client. Only created once."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def synthesize_meeting_brief(
    meeting: dict,
    email_context: str,
    granola_context: str = "",
) -> str:
    """
    Ask Claude to write a brief for a single meeting.
    Returns an HTML string with the meeting section.

    meeting: dict from calendar_client (title, start_time, attendees, etc.)
    email_context: string of relevant email threads from gmail_client
    granola_context: string of relevant notes from granola_client (optional)
    """
    attendee_list = ", ".join(meeting["attendees"]) if meeting["attendees"] else "No external attendees"

    # Build the additional context section
    notes_section = f"\nGRANOLA NOTES:\n{granola_context}" if granola_context else ""

    prompt = f"""You are preparing Will Buehler, a Senior Associate at Camber Partners (a SaaS and AI-focused growth equity firm), for a meeting tomorrow.

MEETING DETAILS:
- Title: {meeting["title"]}
- Time: {meeting["start_time"]} – {meeting["end_time"]}
- Attendees: {attendee_list}
- Description: {meeting["description"] or "No description provided"}
- Location/Link: {meeting["location"] or "Not specified"}

RECENT EMAIL CONTEXT (last 30 days):
{email_context}
{notes_section}

Write a clean, skimmable meeting brief in HTML format. Be concise — Will reads this in 2 minutes over morning coffee. Use this exact structure:

<div class="meeting-section">
  <h3>⏰ {meeting["start_time"]} — {meeting["title"]}</h3>
  <p class="attendees"><strong>With:</strong> [list attendee names/companies, or "Internal team"]</p>
  <p class="why"><em>[One sentence: why this meeting matters to Will at Camber Partners]</em></p>
  <ul>
    <li>[Key context point 1 from emails/notes — be specific, cite actual email details]</li>
    <li>[Key context point 2]</li>
    <li>[Key context point 3, or omit if nothing relevant found]</li>
  </ul>
  <p><strong>💡 Suggested talking point:</strong> [One specific, smart question or point Will could raise]</p>
  [If there are action items: <p><strong>📋 Open items:</strong> [list commitments/follow-ups from email threads]</p>]
</div>

Rules:
- If no email context exists, write "No recent email history — consider sending a prep note beforehand" in the context bullet
- Keep each bullet under 20 words
- Avoid buzzwords and jargon
- If attendees are from a company Will might be evaluating, note the company's focus area if evident from emails
- Output ONLY the HTML div block, nothing else"""

    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def build_full_brief(meetings_with_context: list[dict]) -> str:
    """
    Take a list of meetings (each with their email/granola context already fetched)
    and return the complete HTML brief document.

    Each item in meetings_with_context should have:
    - meeting: dict from calendar_client
    - email_context: string
    - granola_context: string (optional)
    - brief_html: string (will be populated here)
    """
    from datetime import datetime, timedelta, timezone

    et_tz = timezone(timedelta(hours=-4))
    tomorrow = (datetime.now(et_tz) + timedelta(days=1)).strftime("%A, %B %-d, %Y")
    meeting_count = len(meetings_with_context)

    # Generate each meeting's brief section
    brief_sections = []
    for i, item in enumerate(meetings_with_context, 1):
        meeting = item["meeting"]
        print(f"  [{i}/{meeting_count}] Synthesizing brief for: {meeting['title']}")
        section_html = synthesize_meeting_brief(
            meeting=meeting,
            email_context=item["email_context"],
            granola_context=item.get("granola_context", ""),
        )
        brief_sections.append(section_html)

    meetings_html = "\n\n".join(brief_sections)

    # Wrap everything in a clean HTML email template
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 15px;
    line-height: 1.6;
    color: #1a1a1a;
    max-width: 680px;
    margin: 0 auto;
    padding: 20px;
    background: #f9f9f9;
  }}
  .header {{
    background: #1a73e8;
    color: white;
    padding: 20px 24px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
  }}
  .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
  .header p {{ margin: 4px 0 0; opacity: 0.85; font-size: 14px; }}
  .content {{
    background: white;
    padding: 24px;
    border-radius: 0 0 8px 8px;
    border: 1px solid #e0e0e0;
    border-top: none;
  }}
  .meeting-section {{
    border-left: 4px solid #1a73e8;
    padding: 16px 20px;
    margin: 20px 0;
    background: #f8f9ff;
    border-radius: 0 6px 6px 0;
  }}
  .meeting-section h3 {{
    margin: 0 0 8px;
    font-size: 17px;
    color: #1a1a1a;
  }}
  .meeting-section .attendees {{
    margin: 0 0 8px;
    color: #555;
    font-size: 14px;
  }}
  .meeting-section .why {{
    color: #444;
    margin: 0 0 12px;
  }}
  .meeting-section ul {{
    margin: 0 0 12px;
    padding-left: 20px;
  }}
  .meeting-section li {{
    margin-bottom: 4px;
    color: #333;
  }}
  .footer {{
    text-align: center;
    color: #999;
    font-size: 12px;
    margin-top: 20px;
  }}
  .no-meetings {{
    text-align: center;
    padding: 40px;
    color: #555;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>📅 Daily Meeting Brief</h1>
  <p>{tomorrow} &nbsp;·&nbsp; {meeting_count} meeting{"s" if meeting_count != 1 else ""} tomorrow</p>
</div>
<div class="content">
  {meetings_html if meetings_html else '<div class="no-meetings">🎉 No meetings tomorrow — enjoy the open day!</div>'}
</div>
<div class="footer">
  Generated by your Daily Meeting Brief · Powered by Claude AI<br>
  <small>Context sourced from Gmail (last 30 days) and Granola notes</small>
</div>
</body>
</html>"""
