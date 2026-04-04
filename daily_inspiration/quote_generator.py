"""
quote_generator.py

Uses Claude to generate a fresh daily inspirational quote tailored
to how far Will is from his June 21st goal.
"""

import os
import anthropic


_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def generate_quote(days_remaining: int, pct_complete: float) -> dict:
    """
    Generate an original inspirational quote appropriate to where Will
    is in his 79-day journey to June 21st.

    Returns {"quote": str, "theme": str}
    """
    if days_remaining == 0:
        phase = "TODAY IS THE DAY — the goal is reached. Write about the joy and pride of having made it."
    elif days_remaining <= 7:
        phase = f"Only {days_remaining} days left. Write about the final push, the excitement of being almost there, staying strong right at the finish line."
    elif days_remaining <= 21:
        phase = f"{days_remaining} days remain. Write about momentum, how the end is now visible, how each day in this phase matters most."
    elif pct_complete < 25:
        phase = f"Just {round(pct_complete)}% of the way there with {days_remaining} days to go. Write about building habits, the power of showing up consistently early in a journey."
    else:
        phase = f"{round(pct_complete)}% complete with {days_remaining} days remaining. Write about staying the course, the compound effect of daily effort."

    prompt = f"""Write a single short inspirational quote (2-4 sentences max) for Will, who is {days_remaining} days away from a personal goal deadline of June 21st, 2026. He is {round(pct_complete)}% of the way through his journey.

Context for the quote: {phase}

The quote should be about: getting better every day, the happiness that comes from reaching a meaningful goal, perseverance, or the reward waiting at the finish line. Keep it warm, genuine, and specific to where he is in the journey — not generic.

Respond with ONLY the quote text itself, no attribution, no quotation marks, no explanation. Just the 2-4 sentence quote."""

    response = _get_client().messages.create(
        model="claude-opus-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    quote_text = response.content[0].text.strip().strip('"').strip("'")

    return {
        "quote": quote_text,
        "days_remaining": days_remaining,
    }
