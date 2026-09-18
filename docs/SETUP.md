# Setup Guide

A complete, step-by-step guide to running **Jev Telegram Guard** in your own
Telegram groups. No prior Docker or Python experience is required for the
Docker route.

- [What you need](#what-you-need)
- [Step 1 — Create the Telegram bot](#step-1--create-the-telegram-bot)
- [Step 2 — Get an OpenRouter key](#step-2--get-an-openrouter-key)
- [Step 3 — Configure the project](#step-3--configure-the-project)
- [Step 4 — Run the bot](#step-4--run-the-bot)
  - [Option A: Docker (recommended)](#option-a-docker-recommended)
  - [Option B: Local Python](#option-b-local-python)
- [Step 5 — Add the bot to a group](#step-5--add-the-bot-to-a-group)
- [Step 6 — Configure moderation](#step-6--configure-moderation)
- [Step 7 — Verify everything works](#step-7--verify-everything-works)
- [Updating](#updating)
- [Backups](#backups)
- [Switching to PostgreSQL](#switching-to-postgresql)
- [Troubleshooting](#troubleshooting)
- [How to add a language](#how-to-add-a-language)

## What you need

- A Telegram account.
- A computer or server that can stay online (Docker route) **or** Python
  3.10+ (local route).
- An [OpenRouter](https://openrouter.ai) account with a small amount of credit
  (Jev is very cheap — see [costs](#costs)).
- About 10 minutes.

## Step 1 — Create the Telegram bot

1. Open a chat with [@BotFather](https://t.me/BotFather) in Telegram.
2. Send `/newbot` and follow the prompts:
   - **Name**: any display name, e.g. `Jev Guard`.
   - **Username**: must end in `bot`, e.g. `my_jev_guard_bot`.
3. BotFather replies with a **token** that looks like
   `123456789:AA...`. Keep it secret — this is `BOT_TOKEN`.

### Disable privacy mode (important)

By default Telegram bots in groups only receive commands, replies and
mentions — **not normal messages**. Jev Guard needs to read every message.

Send BotFather:

```
/setprivacy
```

Select your bot, then choose **Disable**.

> Alternatively, promote the bot to administrator in the group: admins receive
> all messages even with privacy mode enabled. For a reliable setup do both.

### (Optional) Set the command menu

BotFather will offer to set commands when the bot is created, or you can send
`/setcommands` and select the bot. The bot also registers a localized command
menu on startup, so this is optional.

## Step 2 — Get an OpenRouter key

1. Sign in at [openrouter.ai](https://openrouter.ai).
2. Open [openrouter.ai/keys](https://openrouter.ai/keys) and create a key.
3. Copy it — this is `OPENROUTER_API_KEY`.

The bot uses the **Jev Decisions API** (`~typesafe/jev-latest`) by default.
Without a key the bot still runs in a limited rule-based fallback mode, but
AI detection requires the key.

## Step 3 — Configure the project

Clone the repository and create your environment file:

```bash
git clone https://github.com/Zumka1991/jev-telegram-admin.git
cd jev-telegram-admin
cp .env.example .env
```

Open `.env` in any text editor and fill in at least:

```dotenv
BOT_TOKEN=123456789:AA...your-bot-token...
OPENROUTER_API_KEY=sk-or-v1-...your-openrouter-key...
```

All other values have sensible defaults. See the table in the
[README](../README.md#environment-variables) for the full list.

## Step 4 — Run the bot

### Option A: Docker (recommended)

1. Install Docker Desktop for your platform:
   - Windows / macOS: https://www.docker.com/products/docker-desktop
   - Linux: https://docs.docker.com/engine/install/
2. Make sure Docker is running, then from the project folder:

```bash
docker compose up -d --build
```

3. Watch the logs:

```bash
docker compose logs -f
```

You should see:

```
INFO | app.db.database | База данных готова
INFO | jev | Jev Telegram Guard запущен. Модель: ~typesafe/jev-latest
INFO | aiogram.dispatcher | Run polling for bot @your_bot
```

The container restarts automatically (`restart: unless-stopped`) and the
SQLite database is stored in `./data` on the host.

Stop / start:

```bash
docker compose stop
docker compose start
docker compose down          # remove the container (data stays in ./data)
```

### Option B: Local Python

Requires **Python 3.10 or newer** (3.12 recommended).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

To keep it running after you log out, use a process manager such as
`systemd`, `tmux`, or `supervisor`. Example `systemd` unit
(`/etc/systemd/system/jev-guard.service`):

```ini
[Unit]
Description=Jev Telegram Guard
After=network-online.target

[Service]
WorkingDirectory=/opt/jev-telegram-admin
ExecStart=/opt/jev-telegram-admin/.venv/bin/python -m app.main
Restart=always
User=jev

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now jev-guard
sudo journalctl -u jev-guard -f
```

## Step 5 — Add the bot to a group

1. Open your group → **Add members** → search for your bot's username.
2. Open the group → **Manage** → **Administrators** → **Add admin** → select
   the bot and grant:
   - **Delete messages**
   - **Restrict members**

   These are the minimum rights the bot needs to delete messages, mute and ban.

Once added, the bot posts a greeting and creates default settings for the
chat.

## Step 6 — Configure moderation

An administrator sends:

```
/settings
```

Use the inline buttons:

- **Moderation: on/off** — master switch.
- **Category rows** — tap a category (profanity, insults, fraud, bullying,
  trolling, spam, flood) and choose an action:
  - `off` — ignore;
  - `auto` — the bot picks delete / mute / ban from the severity and Jev's
    recommendation;
  - `warn` — warn (ban when the warning limit is reached);
  - `delete` — delete the message;
  - `mute` — mute the member;
  - `ban` — ban the member.
- **⚙️ Parameters** — confidence threshold, warnings before ban, mute
  duration, whether admins are ignored, notifications.
- **🌐 Language** — switch the interface language for this chat.
- **🩺 Check bot rights** — verify the bot has enough permissions.

> **Admins are ignored by default.** If you test with an administrator
> account, turn off *Ignore admins* in ⚙️ Parameters, or write from a regular
> account.

## Step 7 — Verify everything works

1. Send a benign message like `How are you?` — the bot must **not** touch it.
2. Send an obvious violation from a **non-admin** account (or with
   *Ignore admins* off) and check the bot reacts.
3. Inspect the decision for any text without triggering an action:

```
/check Сука админ падла
```

You get per-category probabilities, the severity, the spam type and Jev's
recommended punishment.

4. Follow the logs:

```bash
docker compose logs -f          # Docker
# or, for the local route, the terminal running python -m app.main
```

Every message the bot receives is logged as `Получено сообщение: ...`,
followed by the decision.

## Missed messages after downtime

Telegram does not let bots read arbitrary chat history. However, while the bot
is offline Telegram queues unconfirmed updates for **up to 24 hours**. On
startup the bot fetches that backlog and processes it through the normal
moderation pipeline (`BACKLOG_ENABLED`, `BACKLOG_MAX_AGE_HOURS`,
`BACKLOG_LIMIT`). Messages older than the retention window cannot be
recovered.

```bash
docker compose logs -f
# Догон пропущенных сообщений: обработано 12, пропущено по возрасту 3
```

## Updating

Pull the latest code and rebuild:

```bash
git pull
docker compose up -d --build
```

The database schema is updated automatically on startup (additive SQLite
migrations).

## Backups

The whole state lives in a single SQLite file at `./data/jev.db`. To back it
up, copy that file:

```bash
docker compose stop
cp data/jev.db "backup/jev-$(date +%F).db"
docker compose start
```

## Switching to PostgreSQL

1. Add `asyncpg` to `requirements.txt`.
2. Set the connection string in `.env`:

```dotenv
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/jev
```

3. Rebuild / restart.

## Troubleshooting

**The bot is in the group but does nothing.**

1. **Privacy mode** — the most common cause. Disable it in BotFather
   (`/setprivacy` → bot → **Disable**) or make the bot an administrator.
2. **Admins are ignored** — *Ignore admins* is on by default; test from a
   non-admin account or turn it off in `/settings` → ⚙️ Parameters.
3. **Missing rights** — grant *Delete messages* and *Restrict members*; check
   with `/settings` → 🩺 Check bot rights.
4. **Moderation disabled** — check the master switch in `/settings`.
5. **Wrong token** — confirm the `BOT_TOKEN` matches the bot you added.

**The bot deletes normal messages.**

- Lower the sensitivity: raise the confidence threshold in
  `/settings` → ⚙️ Parameters.
- Reconsider `auto`: it can be strict. Set the category to `delete` or `warn`
  instead, or disable it with `off`.

**Nothing in the logs when I send a message.**

- The bot is not receiving updates: privacy mode is still on, the bot was not
  added to *this* group, or you are running two instances with the same token
  — stop one of them.

**`OPENROUTER_API_KEY` is missing or invalid.**

- The bot logs a warning at startup and falls back to rule-based detection.
  Add a valid key and restart.

## Costs

Jev is a structural decision model priced at roughly **$0.042 per million
input tokens** (output is free). Each moderated message is one small request,
so even busy groups typically cost cents per month. Set a usage limit in your
OpenRouter account if you want a hard cap.

## How to add a language

Translations live in `app/i18n/locales/<code>.py` as a flat `STRINGS` dict:

1. Copy `en.py` to `<code>.py` and translate the values.
2. Register the locale in `app/i18n/__init__.py`:
   - add it to `LOCALES`, `LANGUAGE_ORDER`, `LANGUAGE_NAMES`, `LANGUAGE_FLAGS`.
3. Rebuild / restart. Users can pick it in `/settings` → 🌐 Language.

English is the fallback for any missing key.
