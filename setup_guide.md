# Daily Meeting Brief — Setup Guide

**Written for Will Buehler | Zero coding experience required**

---

## What You're Building

Every weekday morning at 7am, this tool will:
1. Check your Google Calendar for tomorrow's meetings
2. Search your Gmail for recent emails with each attendee
3. Check your Granola notes for relevant context
4. Ask Claude AI to write a clean, 2-minute brief for each meeting
5. Email the brief to your inbox — automatically, no touching required

**Total setup time: About 90 minutes**

---

## Before You Start — What You'll Need

- A Google account (Gmail + Google Calendar) ✓ already have this
- A GitHub account (free) — we'll create one if needed
- Python installed on your laptop — instructions below
- A credit card for Anthropic (you'll spend less than $2/month)

---

## Part 1 — Create a Google Cloud Project (~30 minutes)

Google requires you to create a "project" to access your own Calendar and Gmail via code. Think of it like registering your app with Google.

### Step 1.1 — Go to Google Cloud Console

1. Open your browser and go to: **https://console.cloud.google.com**
2. Sign in with your Google account (the one with your Calendar and Gmail)
3. If you see "Welcome to Google Cloud" with a button to "Get started for free" — you can click it, but you **do not** need to enter a credit card. Just close that dialog.

### Step 1.2 — Create a New Project

1. In the top bar, click the project dropdown (it might say "My First Project" or show a project name)
2. Click **"New Project"**
3. Name it: **Daily Brief**
4. Leave "Organization" as-is
5. Click **"Create"**
6. Wait about 10 seconds, then make sure "Daily Brief" is selected in the top bar

### Step 1.3 — Enable Google Calendar API

1. In the left sidebar, click **"APIs & Services"** → **"Library"**
2. In the search box, type: **Google Calendar API**
3. Click on "Google Calendar API" in the results
4. Click the blue **"Enable"** button
5. Wait for it to enable (takes about 5 seconds)

### Step 1.4 — Enable Gmail API

1. Go back to the API Library (click "Library" in the left sidebar)
2. Search for: **Gmail API**
3. Click on "Gmail API" → click **"Enable"**

### Step 1.5 — Configure the OAuth Consent Screen

Before creating credentials, Google needs to know what this app is.

1. In the left sidebar, click **"APIs & Services"** → **"OAuth consent screen"**
2. Choose **"External"** and click **"Create"**
3. Fill in:
   - App name: **Daily Brief**
   - User support email: *your email*
   - Developer contact information: *your email*
4. Click **"Save and Continue"** (skip the Scopes page — just click Save and Continue again)
5. On the "Test users" page, click **"+ Add Users"** and add your own Gmail address
6. Click **"Save and Continue"** → **"Back to Dashboard"**

### Step 1.6 — Create OAuth Credentials

1. In the left sidebar, click **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth 2.0 Client IDs"**
3. Application type: **Desktop app**
4. Name: **Daily Brief Desktop**
5. Click **"Create"**
6. A dialog pops up — click **"Download JSON"**
7. Rename the downloaded file to exactly: **`credentials.json`**
8. Move `credentials.json` into your Daily Brief project folder

---

## Part 2 — Get an Anthropic API Key (~5 minutes)

This is what gives you access to Claude AI.

1. Go to: **https://console.anthropic.com**
2. Create an account (or sign in)
3. Go to **"API Keys"** in the left sidebar
4. Click **"Create Key"**
5. Name it: **Daily Brief**
6. **Copy the key immediately** — it starts with `sk-ant-` and you won't be able to see it again
7. Save it somewhere safe (like Apple Notes or 1Password) — you'll need it in Part 4

**Cost:** The app uses Claude Opus (the most capable model). A typical day costs about $0.03–0.10. Monthly cost: well under $3.

---

## Part 3 — Install Python (~10 minutes)

Python is the programming language this app is written in. Even though you won't write any code, you need Python installed to run the one-time setup script.

### Check if Python is already installed

1. Open Terminal (on Mac: press `Cmd + Space`, type "Terminal", press Enter)
2. Type: `python3 --version` and press Enter
3. If you see something like `Python 3.11.x` or higher — you're all set, skip to Part 4

### Install Python (if needed)

1. Go to: **https://python.org/downloads**
2. Click the big yellow **"Download Python 3.x.x"** button
3. Open the downloaded file and follow the installer
4. When asked about "Add Python to PATH" — **check that box** (important!)
5. Click through to finish the installation
6. Close and reopen Terminal, then run `python3 --version` to confirm it worked

---

## Part 4 — Set Up the Project on Your Laptop (~15 minutes)

### Step 4.1 — Get the Project Files

If you haven't already downloaded the project:

1. Go to your GitHub repository (the one where this code lives)
2. Click the green **"Code"** button → **"Download ZIP"**
3. Unzip it and move the folder somewhere easy to find (like your Desktop or Documents)

### Step 4.2 — Open a Terminal in the Project Folder

**On Mac:**
1. Open Finder and navigate to the project folder
2. Right-click the folder → "New Terminal at Folder"

OR:
1. Open Terminal
2. Type `cd ` (with a space), then drag the project folder into the Terminal window, then press Enter

You should see your terminal prompt change to show the project folder name.

### Step 4.3 — Install the Required Libraries

In the terminal (with the project folder open), type:

```
pip3 install -r requirements.txt
```

Press Enter and wait about 30 seconds. You'll see a bunch of text — that's normal.

### Step 4.4 — Create Your .env File

1. In the project folder, find the file called `.env.example`
2. Make a copy of it and name the copy `.env` (no "example")
3. Open `.env` in a text editor (TextEdit on Mac works fine)
4. Fill in your values:
   - `ANTHROPIC_API_KEY` → paste your key from Part 2
   - `BRIEF_RECIPIENT_EMAIL` → your Gmail address (e.g., `will@gmail.com`)
   - Leave `GRANOLA_NOTES_DIR` blank for now (we'll set this up separately)
5. Save the file

### Step 4.5 — Authorize Google (One-Time)

Make sure `credentials.json` is in the project folder, then in Terminal run:

```
python3 scripts/generate_token.py
```

1. Your browser will open to a Google sign-in page
2. Sign in with the Google account you use for Calendar and Gmail
3. You'll see a warning: "Google hasn't verified this app" — click **"Continue"** (this is your own app, it's safe)
4. Check all the permission boxes and click **"Allow"**
5. You'll see "The authentication flow has completed" — go back to Terminal
6. Terminal will show you two things to copy:
   - `GOOGLE_REFRESH_TOKEN` value
   - `GOOGLE_CREDENTIALS` value
7. **Copy both values** — you'll need them in Part 5

---

## Part 5 — Connect to GitHub (~20 minutes)

GitHub is where your code lives and where the automatic scheduling happens (for free).

### Step 5.1 — Create a GitHub Account (if needed)

1. Go to: **https://github.com**
2. Click **"Sign up"**
3. Follow the prompts — use your personal email

### Step 5.2 — Add Your Secrets to GitHub

Your app needs 4 secret values. GitHub keeps these encrypted and hidden.

1. Go to your repository on GitHub
2. Click the **"Settings"** tab (gear icon)
3. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
4. Click **"New repository secret"** for each of the following:

| Secret Name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your key from Part 2 (starts with `sk-ant-`) |
| `GOOGLE_CREDENTIALS` | The JSON blob shown by the setup script |
| `GOOGLE_REFRESH_TOKEN` | The token shown by the setup script |
| `BRIEF_RECIPIENT_EMAIL` | Your Gmail address |

For each one: type the Name, paste the Value, click **"Add secret"**.

---

## Part 6 — Test It (~5 minutes)

Let's make sure everything works before waiting until tomorrow morning.

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. In the left sidebar, click **"Daily Meeting Brief"**
4. Click the **"Run workflow"** button (top right)
5. Click the green **"Run workflow"** button in the popup
6. Wait about 30–60 seconds
7. Refresh the page — you should see a green checkmark ✓

If you see a red ✗ (failure):
- Click on the failed run → click on "send-daily-brief" to see the error log
- The error message will tell you what's wrong
- Common fixes: check that all 4 secrets are added correctly

**Check your inbox!** You should have received an email with your meeting brief.

---

## Part 7 — Automatic Daily Schedule

You don't need to do anything else. The app is now set to run automatically:

- **Every weekday** (Mon–Fri)
- **At 7am Eastern Time**
- **Without you touching anything**

You can verify the schedule is set by going to Actions → Daily Meeting Brief. You'll see the history of runs build up over time.

---

## Optional: Granola Notes Integration

If you use Granola for meeting notes and want to include past notes in your briefs:

1. Open Granola on your Mac
2. Go to Granola's settings and find "Export" or "Notes location"
3. Copy the path to where Granola saves notes (usually `~/Library/Application Support/Granola/notes/`)
4. Add this to your `.env` file:
   ```
   GRANOLA_NOTES_DIR=~/Library/Application Support/Granola/notes/
   ```

Note: Granola notes only work when running the app **locally** (not in GitHub Actions, since Granola lives on your computer). But when you test locally, your briefs will include relevant past meeting notes.

---

## Changing the Daily Run Time

The app runs at 7am ET by default. To change it:

1. Open `.github/workflows/daily_brief.yml` in a text editor
2. Find the line: `- cron: '0 11 * * 1-5'`
3. The format is: `minute hour day month weekday` (all in UTC time)
4. To change the time, modify the `hour` value (UTC = ET + 4 hours in summer, + 5 in winter)
5. Commit and push the change

Examples:
- 6am ET (summer): `0 10 * * 1-5`
- 8am ET (summer): `0 12 * * 1-5`
- Include weekends: `0 11 * * *`

---

## Troubleshooting

**"No meetings found" brief received:**
- Check your Google Calendar — are there events on tomorrow's date?
- Make sure events have attendees (meetings with no attendees are skipped)
- Confirm the timezone in `calendar_client.py` matches your timezone

**"Authentication failed" error:**
- Your Google refresh token may have expired (happens if you change your Google password)
- Re-run `python3 scripts/generate_token.py` and update the GitHub secret

**"ANTHROPIC_API_KEY not found" error:**
- Double-check the secret name in GitHub — it must be exactly `ANTHROPIC_API_KEY`

**Brief arrives but has no email context:**
- This is normal for new contacts or if you haven't emailed them recently
- The AI will still write a brief based on the meeting title and description

**Need help?**
- Check the GitHub Actions run logs (click on the failed run)
- The error messages are usually self-explanatory

---

*Built with Google Calendar API, Gmail API, Granola, and Claude AI by Anthropic.*
