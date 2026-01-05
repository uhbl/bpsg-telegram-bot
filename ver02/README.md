(AI-generated readme, i was very lazy to do it myself)

# BPSG Telegram Bot

A Telegram bot that collects biology olympiad problems from users in a **guided, clean, and consistent** flow and forwards them to admins for review.

---

## Table of Contents
- [Features](#features)
- [How It Works (User Flow)](#how-it-works-user-flow)
- [Repo Structure](#repo-structure)
- [Prerequisites](#prerequisites)
- [1) Create a Telegram Bot (BotFather)](#1-create-a-telegram-bot-botfather)
- [2) Get the Required IDs](#2-get-the-required-ids)
- [3) Configure `bdtbs.py` (Secrets & Dictionaries)](#3-configure-bdtbspy-secrets--dictionaries)
- [4) Run Locally (Python)](#4-run-locally-python)
- [5) Run with Docker](#5-run-with-docker)
  - [5.1 Build directly on Raspberry Pi](#51-build-directly-on-raspberry-pi)
  - [5.2 Cross-build on x86 for Raspberry Pi (arm64)](#52-cross-build-on-x86-for-raspberry-pi-arm64)
  - [5.3 Docker Compose (recommended)](#53-docker-compose-recommended)
- [6) Optional: systemd Service (non-Docker)](#6-optional-systemd-service-non-docker)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- Private, step-by-step submission: **text → media count (0–10) → media → source → year → topic → comments → preview → send**.
- Enforces consistency: **no mixed media types** (either photos or documents), year format validation, source/topic via buttons.
- Works **only in private chats** for safety.
- Lightweight: long-polling, no inbound ports.

**Commands**: `/start`, `/post`, `/cancel`, `/feedback`, `/git`, (`/id` for support).

---

## How It Works (User Flow)
```
/start  → shows welcome + attached user guide
/post   → begins submission wizard
  1) Send problem text (≤ ~900 chars)
  2) Choose media count (0–10)
     • if >0: upload exactly that many files (photos OR documents)
  3) Pick source (button) or skip
  4) Enter year YYYY (e.g., 2024)
  5) Pick topic (button) or type `skip`
  6) Add comments (≤ ~200 chars)
  7) Preview → Yes (send to admins) / No (cancel)
```
Admins receive the problem plus your `@username` and numeric `ID` for follow-up.

---

## Repo Structure
> Adjust names to your repo if different.
```
.
├─ bdtbs.py        # IDs, dictionaries (sources/topics/years), token storage
├─ t.py / test.py  # main bot script (entry point)
├─ requirements.txt
└─ README.md
```

---

## Prerequisites
- Python **3.10+** (tested up to 3.13)
- A Telegram account
- (For Docker) Docker Engine + Docker Compose
- (For Raspberry Pi) Raspberry Pi OS 64-bit recommended (arm64)

---

## 1) Create a Telegram Bot (BotFather)
1. Open Telegram and start chat with **@BotFather**.
2. Send `/newbot` and follow prompts to set **name** and **username**.
3. BotFather will give you a **bot token** (looks like `123456:AA...`). Keep it **secret**.
4. Optional (recommended):
   - `/setprivacy` → **Enable** (bot only receives messages that start with a command in groups; we use private chats anyway).
   - `/setcommands` → define commands list (e.g., `start - show guide`, `post - submit a problem`, `cancel - abort submission`, `feedback - send feedback`, `git - repo link`).

---

## 2) Get the Required IDs
You’ll need:
- **developer_id** (your user ID)
- **test_env_id** (chat ID where submissions are sent; can be your private chat or a private group/channel ID)
- **start_fwd_msg_id** (ID of a pinned/welcome message you want the bot to forward on `/start`)

Ways to get IDs:
- Use a helper bot like **@userinfobot** to get your numeric ID.
- Or add the provided `/id` handler: it prints raw JSON of the incoming message in `<pre>` format. Your chat ID is in there.

> To get `start_fwd_msg_id`, forward a message from your account to the bot or store a specific message in your own chat, then read its `message_id` from JSON (via `/id`) or copy it programmatically.

---

## 3) Configure `bdtbs.py` (Secrets & Dictionaries)
**Never commit real tokens.** Keep `bdtbs.py` out of version control or template it.

Example **`bdtbs.py`** template:
```python
# bdtbs.py — DO NOT COMMIT REAL TOKENS

ids = {
    "bot_api": "123456:AA...",          # BotFather token
    "developer_id": 123456789,           # your Telegram numeric ID
    "start_fwd_msg_id": 111,             # message id to forward on /start
    "test_env_id": 123456789,            # chat id where problems are delivered
}

# Shown as inline keyboard buttons for source
olympiads = {
    "Respa": "Respa",
    "Oblast": "Oblast",
    "Raionka": "Raionka",
    "Junior": "Junior",
    "KBO": "KBO",
    "Vseros": "Vseros",
    "IBO": "IBO",
    "INBO": "INBO",
    "USABO": "USABO",
}

# Topic buttons (values are displayed to users)
topics = {
    "Молекулярная_и_клеточная_биология": "Молекулярная_и_клеточная_биология",
    "Генетика": "Генетика",
    "Биохимия": "Биохимия",
    "Анатомия_и_физиология_животных": "Анатомия_и_физиология_животных",
    "Анатомия_и_физиология_растений": "Анатомия_и_физиология_растений",
    "Эволюция": "Эволюция",
    "Экология": "Экология",
    "Биосистематика": "Биосистематика",
    "Статистика": "Статистика",
    "Зоология": "Зоология",
    "Ботаника": "Ботаника",
    "Другое": "Другое",
}

# Year validation may use a closed range
years = {
    "min": 1990,
    "max": 2027,
}
```

> If your main script imports different shapes (e.g., `years` as strings), adjust accordingly to match the code you ship.

**Security**: put `bdtbs.py` into `.gitignore` and maintain a `bdtbs.example.py` without secrets.

---

## 4) Run Locally (Python)
1. Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

2. Make sure `bdtbs.py` is present and filled in (token, IDs, dictionaries).

3. Run the bot:
```bash
python t.py   # or: python test.py
```

> The bot uses long polling (`infinity_polling()`), so no public ports are needed.

---

## 5) Run with Docker
### Minimal `requirements.txt`
```
pyTelegramBotAPI>=4.17.0
```
Add any extras you use (e.g., `python-dotenv`).

### Dockerfile (multi-arch friendly)
```dockerfile
# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code (do NOT bake secrets here in production)
COPY t.py test.py ./
# Mount bdtbs.py at runtime as a bind or Docker secret; for dev you may copy it:
# COPY bdtbs.py ./

CMD ["python", "t.py"]
```

### 5.1 Build directly on Raspberry Pi
```bash
docker build -t bpsg-bot:latest .
```

### 5.2 Cross-build on x86 for Raspberry Pi (arm64)
```bash
# One-time setup
docker buildx create --use --name bpsg-builder || true

# Build for arm64
docker buildx build \
  --platform linux/arm64 \
  -t bpsg-bot:arm64 \
  --load \
  .
```
If you push to a registry, use `--push` instead of `--load`.

### 5.3 Docker Compose (recommended)
Create **`docker-compose.yml`**:
```yaml
version: "3.9"
services:
  bot:
    image: bpsg-bot:latest   # or your registry/image:tag
    container_name: bpsg-bot
    restart: unless-stopped
    environment:
      - TZ=UTC
    volumes:
      # mount secrets & runtime files
      - ./bdtbs.py:/app/bdtbs.py:ro
      - ./bot.log:/app/bot.log
    # no ports needed; bot uses long polling
```
Then:
```bash
docker compose up -d
```
Check logs:
```bash
docker compose logs -f
```

> **Tip**: keep `bdtbs.py` outside the image and mount it read-only to avoid leaking tokens in your image layers.

---

## 6) Optional: systemd Service (non-Docker)
Create **`/etc/systemd/system/bpsg-bot.service`**:
```ini
[Unit]
Description=BPSG Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/bpsg
ExecStart=/opt/bpsg/.venv/bin/python /opt/bpsg/t.py
Restart=always
RestartSec=3
User=pi
Group=pi
Environment=TZ=UTC

[Install]
WantedBy=multi-user.target
```
Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bpsg-bot
sudo systemctl status bpsg-bot
```

---

## Troubleshooting
- **400: caption is too long** — Telegram limits media captions to ~1024 chars. Keep captions short; send long bodies as normal messages.
- **Message too long** — text messages are limited to ~4096 chars. Split long text.
- **Mixed media rejected** — the bot enforces one media type per submission; restart with `/cancel` then `/post`.
- **No keyboard buttons** — update Telegram, reopen the chat, and run `/post` again.
- **/post in groups doesn’t work** — by design; use a private chat with the bot.
- **Token invalid** — re-check `ids["bot_api"]` in `bdtbs.py` or rotate token via @BotFather.

---

## Security Notes
- **Never commit tokens**. Keep `bdtbs.py` local and in `.gitignore`; publish `bdtbs.example.py` instead.
- Prefer mounting `bdtbs.py` into the container rather than copying it into the image.
- Rotate tokens from @BotFather if you suspect a leak.
- Least privilege: use a throwaway admin/test chat for `test_env_id` before moving to production channels.

---

## Contributing
PRs and issues are welcome. Please:
- Describe the context and logs (redact secrets).
- Propose minimal reproducible examples.
- Follow the existing code style (black/PEP8-friendly).

---

## License
Specify your license here (e.g., MIT). Add a `LICENSE` file in the repo root.

