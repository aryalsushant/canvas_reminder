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

The bot needs to run continuously to catch reminders. A few options:

### Cron job (simplest, for always-on machines)

```bash
# Run at reboot; redirect logs to a file
@reboot cd /path/to/canvas_reminder && /usr/bin/python3 main.py >> bot.log 2>&1
```

Add this with `crontab -e`.

### PythonAnywhere

1. Upload the project to PythonAnywhere.
2. Go to the **Tasks** tab and create a scheduled task that runs `python main.py`.
3. PythonAnywhere free-tier scheduled tasks run once daily — for true continuous operation, upgrade to a paid plan and use an **Always-on task**.

### VPS with systemd

Create `/etc/systemd/system/canvas-reminder.service`:

```ini
[Unit]
Description=Canvas Assignment Reminder Bot
After=network.target

[Service]
WorkingDirectory=/path/to/canvas_reminder
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable canvas-reminder
sudo systemctl start canvas-reminder
sudo systemctl status canvas-reminder
```

### VPS with screen or tmux

```bash
# With screen
screen -S canvas-bot
python main.py
# Detach: Ctrl+A then D

# With tmux
tmux new -s canvas-bot
python main.py
# Detach: Ctrl+B then D
```

---

## Security

- **Never commit `.env`** — it contains your API tokens. The `.gitignore` in this project excludes it, but double-check before pushing.
- **Never share your tokens** — anyone with your Canvas token can read your courses and submissions; anyone with your Telegram token can send messages as your bot.
- Rotate your tokens immediately if you suspect they've been exposed.
- `sent_reminders.json` contains assignment names and IDs — it is also excluded from git.
