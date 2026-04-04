"""
email_builder.py

Assembles the full HTML earnings digest email from individual company sections.
"""

from datetime import date, timedelta
from earnings_digest.tickers import ETF_HOLDINGS


def _week_label() -> str:
    """Returns a label like 'April 7 – April 13, 2026'."""
    today = date.today()
    week_start = today - timedelta(days=7)
    if week_start.month == today.month:
        return f"{week_start.strftime('%B %-d')} \u2013 {today.strftime('%-d, %Y')}"
    return f"{week_start.strftime('%B %-d')} \u2013 {today.strftime('%B %-d, %Y')}"


def _build_upcoming_section(upcoming: list[dict]) -> str:
    """Build the 'Reporting Next Week' section HTML."""
    if not upcoming:
        return ""

    rows = ""
    for item in upcoming:
        ticker = item.get("ticker", "")
        company = item.get("company", "")
        date_str = item.get("expected_date_str", item.get("expected_date", ""))
        time_of_day = item.get("time_of_day", "")
        time_label = ""
        if time_of_day and time_of_day != "unconfirmed":
            time_label = f' <span style="color:#aaa; font-size:11px;">({time_of_day})</span>'

        rows += f"""
        <tr>
          <td style="padding:8px 0; border-bottom:1px solid #f0f0ea;">
            <span style="background-color:#2d4a6e; color:#ffffff; font-family:monospace; font-size:11px; font-weight:bold; padding:2px 6px; border-radius:3px;">{ticker}</span>
            <span style="font-family:Arial,sans-serif; font-size:13px; color:#2a2a3e; margin-left:8px;">{company}</span>
          </td>
          <td style="padding:8px 0; border-bottom:1px solid #f0f0ea; text-align:right; font-family:Arial,sans-serif; font-size:13px; color:#555;">
            {date_str}{time_label}
          </td>
        </tr>"""

    return f"""
<div style="margin-bottom:24px; border:1px solid #e0e0d8; border-radius:8px; overflow:hidden;">
  <div style="background-color:#2d4a6e; padding:14px 20px;">
    <p style="margin:0; font-size:13px; font-weight:bold; color:#ffffff; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">
      &#128197; Reporting Next Week
    </p>
  </div>
  <div style="padding:4px 20px 4px; background-color:#ffffff;">
    <table width="100%" cellpadding="0" cellspacing="0">
      {rows}
    </table>
  </div>
</div>
"""


def build_earnings_html(company_sections: list[str], tickers_checked: list[str], upcoming: list[dict] | None = None) -> str:
    """
    Build the full HTML email.

    company_sections: list of HTML strings, one per company that reported
    tickers_checked: list of tickers that were scanned (for footer)
    upcoming: list of dicts for companies reporting next week (from fetch_upcoming_earnings)
    """
    try:
        week = _week_label()
    except Exception:
        week = str(date.today())

    n = len(company_sections)
    report_count = f"{n} report{'s' if n != 1 else ''}" if n > 0 else "no reports"

    upcoming_html = _build_upcoming_section(upcoming or [])

    if n == 0:
        body_html = """
        <div style="text-align:center; padding:40px 24px; color:#888; font-family:Arial,sans-serif;">
          <p style="font-size:32px; margin:0;">&#128203;</p>
          <p style="font-size:18px; color:#555; margin:12px 0 8px;">No earnings this week</p>
          <p style="font-size:14px; color:#aaa; margin:0;">None of your portfolio companies reported earnings in the past 7 days.</p>
        </div>"""
    else:
        body_html = "\n".join(company_sections)

    body_html += upcoming_html

    etf_list = ", ".join(f"{t} ({n})" for t, n in ETF_HOLDINGS.items())
    ticker_list = ", ".join(tickers_checked)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weekly Earnings Digest</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f0; font-family:Georgia,'Times New Roman',serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f0; padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="620" cellpadding="0" cellspacing="0" style="max-width:620px; width:100%;">

          <!-- Header -->
          <tr>
            <td style="background-color:#1a1a2e; border-radius:12px 12px 0 0; padding:28px 36px 24px;">
              <p style="margin:0; font-size:13px; color:#a0a8c0; letter-spacing:1px; text-transform:uppercase; font-family:Arial,sans-serif;">
                &#128202; Weekly Earnings Digest
              </p>
              <p style="margin:8px 0 0; font-size:22px; color:#ffffff; font-family:Arial,sans-serif; font-weight:bold;">
                {week}
              </p>
              <p style="margin:6px 0 0; font-size:13px; color:#a0a8c0; font-family:Arial,sans-serif;">
                {report_count} from your portfolio
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background-color:#f8f8f4; padding:24px 24px 0; border-left:1px solid #e0e0d8; border-right:1px solid #e0e0d8;">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f0f0ea; border:1px solid #e0e0d8; border-top:none; border-radius:0 0 12px 12px; padding:20px 36px;">
              <p style="margin:0 0 6px; font-size:12px; color:#888; font-family:Arial,sans-serif; font-weight:bold;">Stocks monitored:</p>
              <p style="margin:0 0 12px; font-size:11px; color:#aaa; font-family:Arial,sans-serif;">{ticker_list}</p>
              <p style="margin:0 0 6px; font-size:12px; color:#888; font-family:Arial,sans-serif; font-weight:bold;">ETF holdings (no earnings):</p>
              <p style="margin:0 0 16px; font-size:11px; color:#aaa; font-family:Arial,sans-serif;">{etf_list}</p>
              <p style="margin:0; font-size:11px; color:#bbb; font-family:Arial,sans-serif; font-style:italic;">
                Earnings data sourced from public financial reports via web search. This email is for informational purposes only and does not constitute investment advice.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""

    return html
