"""
synthesizer.py

Takes raw earnings data and asks Claude to write a full deep-dive HTML section
covering all key metrics, management commentary, and analyst reactions.
"""

import os
import anthropic


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def synthesize_earnings_report(raw: dict) -> str:
    """
    Given raw earnings data dict from earnings_fetcher, produce a complete
    HTML section with a full deep-dive analysis.
    Returns an HTML string (a self-contained <div> block).
    """
    ticker = raw.get("ticker", "")
    company = raw.get("company", "")
    quarter = raw.get("quarter", "")

    beats = []
    misses = []
    if raw.get("revenue_beat_miss") == "beat":
        beats.append(f"Revenue ({raw.get('revenue_actual')} vs est. {raw.get('revenue_estimate')})")
    elif raw.get("revenue_beat_miss") == "missed":
        misses.append(f"Revenue ({raw.get('revenue_actual')} vs est. {raw.get('revenue_estimate')})")

    if raw.get("eps_beat_miss") == "beat":
        beats.append(f"EPS ({raw.get('eps_actual')} vs est. {raw.get('eps_estimate')})")
    elif raw.get("eps_beat_miss") == "missed":
        misses.append(f"EPS ({raw.get('eps_actual')} vs est. {raw.get('eps_estimate')})")

    beat_miss_color = "#2d6a4f" if beats and not misses else ("#c1121f" if misses else "#555")
    beat_miss_label = "Beat on all fronts" if beats and not misses else (
        "Mixed results" if beats and misses else (
        "Missed estimates" if misses else "In-line with estimates"
    ))

    highlights_html = ""
    for h in raw.get("key_highlights", []):
        highlights_html += f'<li style="margin-bottom:6px;">{h}</li>'

    # Build the HTML section directly (no second Claude call needed)
    gross_margin = raw.get("gross_margin", "N/A")
    gross_margin_chg = raw.get("gross_margin_yoy_change", "")
    gross_margin_str = f"{gross_margin}" + (f" ({gross_margin_chg} YoY)" if gross_margin_chg and gross_margin_chg != "N/A" else "")

    op_margin = raw.get("operating_margin", "N/A")
    rev_growth = raw.get("revenue_yoy_growth", "N/A")
    guidance = raw.get("guidance_summary", "No guidance provided")
    mgmt = raw.get("management_commentary", "")
    analysts = raw.get("analyst_reaction", "")
    risks = raw.get("notable_risks", "")
    source = raw.get("source_url", "")

    html = f"""
<div style="margin-bottom:32px; border:1px solid #e0e0d8; border-radius:8px; overflow:hidden;">

  <!-- Company header -->
  <div style="background-color:#1a1a2e; padding:16px 24px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td>
          <span style="background-color:#4a7c59; color:#ffffff; font-family:monospace; font-size:13px; font-weight:bold; padding:3px 8px; border-radius:4px;">{ticker}</span>
          <span style="color:#ffffff; font-size:18px; font-weight:bold; margin-left:10px; font-family:Arial,sans-serif;">{company}</span>
        </td>
        <td align="right">
          <span style="color:#a0a8c0; font-size:13px; font-family:Arial,sans-serif;">{quarter}</span>
        </td>
      </tr>
    </table>
    <p style="margin:8px 0 0; font-family:Arial,sans-serif; font-size:13px; font-weight:bold; color:{beat_miss_color}; background-color:rgba(255,255,255,0.08); display:inline-block; padding:2px 10px; border-radius:3px;">
      {beat_miss_label}
    </p>
  </div>

  <!-- Key metrics row -->
  <div style="background-color:#f8f8f4; padding:16px 24px; border-bottom:1px solid #e0e0d8;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td width="25%" style="padding-right:12px;">
          <p style="margin:0; font-size:11px; color:#888; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Revenue</p>
          <p style="margin:4px 0 0; font-size:16px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif;">{raw.get('revenue_actual','N/A')}</p>
          <p style="margin:2px 0 0; font-size:11px; color:#888; font-family:Arial,sans-serif;">est. {raw.get('revenue_estimate','N/A')}</p>
        </td>
        <td width="25%" style="padding-right:12px;">
          <p style="margin:0; font-size:11px; color:#888; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">EPS</p>
          <p style="margin:4px 0 0; font-size:16px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif;">{raw.get('eps_actual','N/A')}</p>
          <p style="margin:2px 0 0; font-size:11px; color:#888; font-family:Arial,sans-serif;">est. {raw.get('eps_estimate','N/A')}</p>
        </td>
        <td width="25%" style="padding-right:12px;">
          <p style="margin:0; font-size:11px; color:#888; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Gross Margin</p>
          <p style="margin:4px 0 0; font-size:16px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif;">{gross_margin_str}</p>
        </td>
        <td width="25%">
          <p style="margin:0; font-size:11px; color:#888; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Revenue Growth YoY</p>
          <p style="margin:4px 0 0; font-size:16px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif;">{rev_growth}</p>
        </td>
      </tr>
    </table>
  </div>

  <!-- Body content -->
  <div style="padding:20px 24px; background-color:#ffffff;">

    <!-- Highlights -->
    <p style="margin:0 0 8px; font-size:13px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Key Highlights</p>
    <ul style="margin:0 0 20px; padding-left:20px; font-family:Georgia,serif; font-size:14px; color:#2a2a3e; line-height:1.6;">
      {highlights_html}
    </ul>

    <!-- Guidance -->
    <p style="margin:0 0 6px; font-size:13px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Forward Guidance</p>
    <p style="margin:0 0 20px; font-family:Georgia,serif; font-size:14px; color:#2a2a3e; line-height:1.6;">{guidance}</p>

    <!-- Management commentary -->
    {f'''<p style="margin:0 0 6px; font-size:13px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Management Commentary</p>
    <p style="margin:0 0 20px; font-family:Georgia,serif; font-size:14px; color:#2a2a3e; line-height:1.6; border-left:3px solid #4a7c59; padding-left:12px; font-style:italic;">{mgmt}</p>''' if mgmt else ''}

    <!-- Analyst reaction -->
    {f'''<p style="margin:0 0 6px; font-size:13px; font-weight:bold; color:#1a1a2e; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Analyst Reaction</p>
    <p style="margin:0 0 20px; font-family:Georgia,serif; font-size:14px; color:#2a2a3e; line-height:1.6;">{analysts}</p>''' if analysts else ''}

    <!-- Risks -->
    {f'''<p style="margin:0 0 6px; font-size:13px; font-weight:bold; color:#c1121f; font-family:Arial,sans-serif; text-transform:uppercase; letter-spacing:0.5px;">Notable Risks / Concerns</p>
    <p style="margin:0 0 12px; font-family:Georgia,serif; font-size:14px; color:#2a2a3e; line-height:1.6;">{risks}</p>''' if risks else ''}

    <!-- Source -->
    {f'<p style="margin:0; font-size:11px; color:#aaa; font-family:Arial,sans-serif;"><a href="{source}" style="color:#4a7c59;">View source</a></p>' if source else ''}

  </div>
</div>
"""
    return html
