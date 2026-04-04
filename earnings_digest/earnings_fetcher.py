"""
earnings_fetcher.py

Uses Claude with web_search to find earnings reports published in the past 7 days
for each ticker. Returns structured data or None if no recent report found.
"""

import json
import os
from datetime import date, timedelta

import anthropic


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def fetch_recent_earnings(ticker: str, company: str) -> dict | None:
    """
    Search the web for a quarterly earnings report for this company
    published in the past 7 days.

    Returns a structured dict with raw earnings data, or None if no
    report was found in the past week.
    """
    today = date.today()
    week_ago = today - timedelta(days=7)
    today_str = today.strftime("%B %d, %Y")
    week_ago_str = week_ago.strftime("%B %d, %Y")

    prompt = f"""Today is {today_str}. Search the web for {company} ({ticker}) quarterly earnings results that were reported between {week_ago_str} and {today_str}.

If you find a recent earnings report (published within the last 7 days), extract and return the following as a JSON object:
{{
  "found": true,
  "ticker": "{ticker}",
  "company": "{company}",
  "report_date": "YYYY-MM-DD",
  "quarter": "Q1/Q2/Q3/Q4 YYYY",
  "revenue_actual": "$X.XB or $X.XM",
  "revenue_estimate": "$X.XB or $X.XM",
  "revenue_beat_miss": "beat / missed / in-line",
  "eps_actual": "$X.XX",
  "eps_estimate": "$X.XX",
  "eps_beat_miss": "beat / missed / in-line",
  "gross_margin": "XX%",
  "gross_margin_yoy_change": "+/-XXbps or N/A",
  "operating_margin": "XX% or N/A",
  "revenue_yoy_growth": "+/-XX%",
  "guidance_summary": "Brief summary of forward guidance or 'No guidance provided'",
  "key_highlights": ["bullet 1", "bullet 2", "bullet 3"],
  "management_commentary": "1-2 key quotes or themes from the earnings call",
  "analyst_reaction": "Brief summary of analyst sentiment and any rating changes",
  "notable_risks": "Any risks or negatives mentioned",
  "source_url": "URL of the primary source"
}}

If NO earnings report was published in the past 7 days for this company, return:
{{"found": false, "ticker": "{ticker}", "company": "{company}"}}

Return ONLY the JSON object, no other text."""

    try:
        response = _get_client().messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response (may come after tool use)
        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text = block.text.strip()
                break

        if not result_text:
            return None

        # Parse JSON response
        # Strip markdown code fences if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]

        data = json.loads(result_text.strip())

        if not data.get("found"):
            return None

        return data

    except Exception as e:
        print(f"  Warning: Could not fetch earnings for {ticker}: {e}")
        return None
