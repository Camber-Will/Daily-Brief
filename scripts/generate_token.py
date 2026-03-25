"""
generate_token.py

One-time setup script: authorizes this app to access your Google Calendar and Gmail.

HOW IT WORKS:
1. You run this script once on your laptop
2. A browser window opens asking you to sign in to Google and click "Allow"
3. Google gives this app a "refresh token" — like a permanent pass
4. You copy that refresh token into GitHub Secrets
5. After that, the app can run automatically in the cloud forever

TO RUN THIS SCRIPT:
  1. Make sure credentials.json is in the root project folder
  2. In your terminal, run:  python scripts/generate_token.py
  3. Follow the browser prompts
  4. Copy the GOOGLE_REFRESH_TOKEN value shown at the end
"""

import json
import os
import sys

# Make sure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# The permissions we need — read calendar, read/send email
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def main():
    print("=" * 60)
    print("Google OAuth Setup — Daily Meeting Brief")
    print("=" * 60)
    print()

    # Check for credentials.json
    if not os.path.exists("credentials.json"):
        print("ERROR: credentials.json not found in the current directory.")
        print()
        print("To get credentials.json:")
        print("  1. Go to: https://console.cloud.google.com")
        print("  2. Create a project called 'Daily Brief'")
        print("  3. Enable: Google Calendar API and Gmail API")
        print("  4. Go to APIs & Services → Credentials")
        print("  5. Click 'Create Credentials' → 'OAuth 2.0 Client ID'")
        print("  6. Choose 'Desktop app', name it 'Daily Brief'")
        print("  7. Download the JSON file and rename it 'credentials.json'")
        print("  8. Put it in this project folder")
        print("  9. Run this script again")
        sys.exit(1)

    print("Found credentials.json ✓")
    print()
    print("Opening your browser for Google sign-in...")
    print("(If the browser doesn't open automatically, check the terminal for a URL to copy/paste)")
    print()

    # Run the OAuth flow — this opens a browser window
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)

    # Save the full token for local development
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("Saved token.json for local development ✓")

    # Parse the token to extract what we need
    token_data = json.loads(creds.to_json())
    refresh_token = token_data.get("refresh_token", "")

    # Read the client credentials for the secrets guide
    with open("credentials.json") as f:
        creds_data = json.load(f)

    print()
    print("=" * 60)
    print("SUCCESS! Now add these to GitHub Secrets:")
    print("=" * 60)
    print()
    print("Go to: Your GitHub repo → Settings → Secrets and variables → Actions")
    print("Click 'New repository secret' for each one below:")
    print()
    print(f"Secret name:  GOOGLE_REFRESH_TOKEN")
    print(f"Secret value: {refresh_token}")
    print()
    print(f"Secret name:  GOOGLE_CREDENTIALS")
    with open("credentials.json") as f:
        raw = f.read().replace("\n", "").replace("  ", "")
    print(f"Secret value: {raw}")
    print()
    print("=" * 60)
    print("Also add these two secrets:")
    print()
    print("  ANTHROPIC_API_KEY    → your key from console.anthropic.com")
    print("  BRIEF_RECIPIENT_EMAIL → your Gmail address (e.g., will@gmail.com)")
    print("=" * 60)
    print()
    print("All done! Your app is ready to run automatically.")


if __name__ == "__main__":
    main()
