# Canvas Assignment Reminder Bot

A lightweight Python bot that watches your Canvas LMS for upcoming assignment deadlines and sends you a message on Telegram before each one is due. Set it up once, leave it running, and never miss a deadline again.

> The bot reads directly from the **Assignments** section of each course — not the calendar. As long as the professor created the assignment in Canvas with a due date, the bot will catch it.

---

## Quick Setup

### Step 1 — Fork this repo

Click **Fork** at the top-right of this GitHub page to get your own copy.

---

### Step 2 — Get your Canvas API token

1. Log in to Canvas and click your profile picture (top-left).
2. Go to **Account → Settings**.
3. Scroll down to **Approved Integrations** and click **+ New Access Token**.
4. Give it a name (e.g., "Reminder Bot") and click **Generate Token**.
5. Copy the token immediately — Canvas won't show it again.

> Official guide: https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273

---

### Step 3 — Create a Telegram bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts (choose a name and a username ending in `bot`).
3. BotFather will give you a token like `123456789:ABC-DEF...`. Copy it.

---

### Step 4 — Find your Telegram chat ID

1. Send any message to your new bot (e.g., "hi").
2. Open this URL in your browser (replace `<YOUR_BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Find `"chat": {"id": 123456789, ...}` — that number is your chat ID.

---

### Step 5 — Deploy on Railway (free, runs 24/7)

This is the recommended way to run the bot — it stays alive even when your computer is off.

1. Sign up at [railway.app](https://railway.app) and connect your GitHub account.
2. Click **New Project → Deploy from GitHub repo** and select your forked repo.
3. Once deployed, go to your service → **Variables** tab and add the following:

| Variable | Value |
|---|---|
| `CANVAS_API_URL` | Your Canvas URL, e.g. `https://myschool.instructure.com` |
| `CANVAS_API_TOKEN` | Token from Step 2 |
| `TELEGRAM_BOT_TOKEN` | Token from Step 3 |
| `TELEGRAM_CHAT_ID` | Chat ID from Step 4 |
| `TIMEZONE` | Your timezone, e.g. `America/New_York` — see [full list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) |
| `REMINDER_HOURS_BEFORE` | How many hours before the deadline to notify you (e.g. `4`) |
| `CHECK_INTERVAL_MINUTES` | How often to check Canvas in minutes (e.g. `150`) |
| `CANVAS_COURSE_IDS` | Optional — leave blank to monitor all active courses |

4. Save the variables — Railway will redeploy automatically and the bot starts running.

---

### Step 6 — Verify it's working

In Railway, go to your service → **Logs** tab. A healthy bot looks like:

```
Canvas Reminder Bot started. Checking every 150 minute(s), reminding 4.0 hour(s) before due dates.
Checking for upcoming assignments…
Found 6 upcoming assignment(s)
Next check in 150 minute(s).
```

When an assignment is within your reminder window, you'll get a Telegram message like:

```
🔔 Assignment Reminder

📝 Homework 3
📚 MATH 101
⏰ Due: Today at 11:59 PM
⌛ Time remaining: 3 hours 42 minutes

View Assignment
```

---

## Running locally (optional)

If you want to run it on your own machine instead:

```bash
git clone https://github.com/yourusername/canvas_reminder
cd canvas_reminder
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your values
python main.py
```

---

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `CANVAS_API_URL` | required | Base URL of your Canvas instance |
| `CANVAS_API_TOKEN` | required | Your Canvas personal access token |
| `TELEGRAM_BOT_TOKEN` | required | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | required | Your personal Telegram chat ID |
| `TIMEZONE` | `UTC` | Your local timezone for display (IANA format) |
| `REMINDER_HOURS_BEFORE` | `3` | Hours before deadline to send reminder |
| `CHECK_INTERVAL_MINUTES` | `30` | How often to check Canvas |
| `CANVAS_COURSE_IDS` | _(empty)_ | Comma-separated course IDs — blank = all active courses |

---

## Security

- **Never commit `.env`** — it contains your API tokens. The `.gitignore` excludes it automatically.
- **Never share your tokens** — anyone with your Canvas token can read your courses and submissions.
- Rotate your tokens immediately if you suspect they've been exposed.
- `sent_reminders.json` contains assignment data — it is also excluded from git.
