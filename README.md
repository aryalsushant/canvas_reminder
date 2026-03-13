# Canvas Assignment Reminder Bot

A lightweight Python bot that watches your Canvas LMS for upcoming assignment deadlines and sends you a Telegram message a configurable number of hours before each one is due. Set it up once, leave it running, and never miss a deadline again.

---

## Prerequisites

- Python 3.8 or later
- A Canvas account with API access (most institutional accounts have this)
- A Telegram account

---

## Setup

### 1. Get your Canvas API token

1. Log in to Canvas and click your profile picture (top-left).
2. Go to **Account → Settings**.
3. Scroll down to **Approved Integrations** and click **+ New Access Token**.
4. Give it a name (e.g., "Reminder Bot") and click **Generate Token**.
5. Copy the token immediately — Canvas won't show it again.

> Official guide: https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273

---

### 2. Create a Telegram bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts (choose a name and username).
3. BotFather will give you an API token that looks like `123456789:ABC-DEF...`. Copy it.

---

### 3. Find your Telegram chat ID

1. Send any message to your new bot (e.g., "hello").
2. Open this URL in your browser (replace `<YOUR_BOT_TOKEN>`):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for `"chat": {"id": 123456789, ...}` — that number is your chat ID.

---

### 4. Find your Canvas course IDs (optional)

If you want to monitor only specific courses instead of all active ones:

1. In Canvas, open a course.
2. Look at the URL: `https://myschool.instructure.com/courses/12345` — the number at the end is the course ID.
3. List multiple IDs separated by commas in `CANVAS_COURSE_IDS`.

Leave `CANVAS_COURSE_IDS` blank to automatically monitor all active courses.

---

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
CANVAS_API_URL=https://myschool.instructure.com
CANVAS_API_TOKEN=your_canvas_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
REMINDER_HOURS_BEFORE=3
CHECK_INTERVAL_MINUTES=30
CANVAS_COURSE_IDS=          # optional
```

---

### 6. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 7. Run the bot

```bash
python main.py
```

You should see log output like:

```
2024-03-15 10:00:00 [INFO] __main__: Canvas Reminder Bot started. Checking every 30 minute(s), reminding 3.0 hour(s) before due dates.
2024-03-15 10:00:00 [INFO] __main__: Checking for upcoming assignments…
```

---

## Deploying for continuous operation

The bot needs to run continuously to catch reminders. This project is deployed on **Railway**, which keeps it running 24/7 in the cloud — even when your computer is off.

### Railway (recommended)

1. Push this repo to GitHub (use a **private** repository to keep your code safe).
2. Sign up at [railway.app](https://railway.app) and connect your GitHub account.
3. Click **New Project → Deploy from GitHub repo** and select this repository.
4. Once deployed, go to your service → **Variables** tab and add all the values from `.env.example` with your real credentials.
5. Railway will redeploy automatically and the bot will start running.

The `Procfile` in this repo tells Railway how to start the bot:

```
worker: python main.py
```

You can monitor live output under the **Logs** tab in your Railway service. A healthy bot looks like:

```
Canvas Reminder Bot started. Checking every 30 minute(s), reminding 3.0 hour(s) before due dates.
Checking for upcoming assignments…
Found 6 upcoming assignment(s)
Next check in 30 minute(s).
```

> **Note:** Do not set `CHECK_INTERVAL_MINUTES` to a large value like 720 (12 hours). The bot needs to check frequently enough to catch the reminder window. 30 minutes is a safe default for a 3-hour reminder window.

### Other options

- **Cron job** — if you have an always-on machine, add `@reboot cd /path/to/canvas_reminder && python3 main.py >> bot.log 2>&1` via `crontab -e`.
- **VPS with systemd** — clone the repo on any Linux VPS and run it as a systemd service.
- **PythonAnywhere** — free tier only supports once-daily scheduled tasks, not continuous loops. Requires a paid plan for always-on tasks.

---

## Security

- **Never commit `.env`** — it contains your API tokens. The `.gitignore` in this project excludes it, but double-check before pushing.
- **Never share your tokens** — anyone with your Canvas token can read your courses and submissions; anyone with your Telegram token can send messages as your bot.
- Rotate your tokens immediately if you suspect they've been exposed.
- `sent_reminders.json` contains assignment names and IDs — it is also excluded from git.
