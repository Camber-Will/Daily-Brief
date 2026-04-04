"""
email_builder.py

Builds the HTML email for the daily inspiration message.
Designed to render cleanly in Gmail and most email clients.
"""

from datetime import date


def _progress_bar(pct: float, width: int = 30) -> str:
    """Generate an email-safe HTML progress bar."""
    filled = round(pct / 100 * width)
    empty = width - filled
    filled_bar = "&#9608;" * filled   # █
    empty_bar = "&#9617;" * empty     # ░
    return f"{filled_bar}{empty_bar}"


def build_inspiration_html(progress: dict, quote: dict) -> str:
    """
    Build the full HTML email body.

    progress: from tracker.get_progress()
    quote: from quote_generator.generate_quote()
    """
    today = progress["today"]
    days_remaining = progress["days_remaining"]
    days_elapsed = progress["days_elapsed"]
    pct = progress["pct_complete"]
    total = progress["total_days"]

    day_label = "day" if days_remaining == 1 else "days"
    today_str = today.strftime("%A, %B %-d, %Y") if hasattr(today, 'strftime') else str(today)

    # Try Windows-safe date formatting
    try:
        today_str = today.strftime("%A, %B %d, %Y").replace(" 0", " ")
    except Exception:
        today_str = str(today)

    bar = _progress_bar(pct)
    goal_date = "June 21, 2026"

    if days_remaining == 0:
        countdown_text = "&#127881; You made it. Today is the day."
        countdown_sub = "June 21st has arrived. You did the work."
    else:
        countdown_text = f"<strong>{days_remaining} {day_label}</strong> until {goal_date}"
        countdown_sub = f"Day {days_elapsed} of {total} &nbsp;&#183;&nbsp; {pct}% complete"

    quote_text = quote["quote"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your Morning Fuel</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f0; font-family: Georgia, 'Times New Roman', serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f0; padding: 32px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px; width:100%;">

          <!-- Header -->
          <tr>
            <td style="background-color:#1a1a2e; border-radius:12px 12px 0 0; padding: 28px 36px 24px;">
              <p style="margin:0; font-size:13px; color:#a0a8c0; letter-spacing:1px; text-transform:uppercase; font-family: Arial, sans-serif;">
                &#127749; Good Morning, Will
              </p>
              <p style="margin:8px 0 0; font-size:15px; color:#d0d4e8; font-family: Arial, sans-serif;">
                {today_str}
              </p>
            </td>
          </tr>

          <!-- Countdown -->
          <tr>
            <td style="background-color:#ffffff; padding: 32px 36px 24px; border-left: 1px solid #e8e8e0; border-right: 1px solid #e8e8e0;">
              <p style="margin:0; font-size:30px; color:#1a1a2e; line-height:1.2; font-weight:normal;">
                {countdown_text}
              </p>
              <p style="margin:8px 0 0; font-size:14px; color:#888; font-family: Arial, sans-serif;">
                {countdown_sub}
              </p>
            </td>
          </tr>

          <!-- Progress Bar -->
          <tr>
            <td style="background-color:#ffffff; padding: 0 36px 28px; border-left: 1px solid #e8e8e0; border-right: 1px solid #e8e8e0;">
              <div style="background-color:#f0f0ea; border-radius:4px; padding: 14px 16px; font-family: 'Courier New', Courier, monospace;">
                <span style="color:#4a7c59; font-size:18px; letter-spacing:1px;">{_progress_bar(pct, 28)}</span>
                <span style="color:#888; font-size:13px; margin-left:10px; font-family: Arial, sans-serif;">{pct}%</span>
              </div>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="background-color:#ffffff; padding: 0 36px; border-left: 1px solid #e8e8e0; border-right: 1px solid #e8e8e0;">
              <hr style="border:none; border-top:1px solid #e8e8e0; margin:0 0 28px;">
            </td>
          </tr>

          <!-- Quote -->
          <tr>
            <td style="background-color:#ffffff; padding: 0 36px 36px; border-left: 1px solid #e8e8e0; border-right: 1px solid #e8e8e0;">
              <table cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td style="border-left: 4px solid #4a7c59; padding-left: 20px;">
                    <p style="margin:0; font-size:19px; line-height:1.65; color:#2a2a3e; font-style:italic;">
                      &#8220;{quote_text}&#8221;
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f8f8f4; border: 1px solid #e8e8e0; border-top: none; border-radius: 0 0 12px 12px; padding: 20px 36px; text-align:center;">
              <p style="margin:0; font-size:13px; color:#999; font-family: Arial, sans-serif; font-style:italic;">
                You've got this. &mdash; Your daily reminder
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
