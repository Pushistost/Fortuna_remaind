# Fortuna Telegram Bot

This project contains a Telegram bot that stores reminders in a local SQLite database.

## Installation

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment variables in a `.env` file. See `tgbot/config.py` for required variables.

## Initialising the database

The bot uses a SQLite database located at `sqlite/db.sqlite3`. When the bot starts
it automatically creates all tables by calling `make_base()` from
`sqlite.models`. If you need to initialise the database manually, you can run the
following snippet:

```bash
python - <<'PY'
import asyncio
from sqlite.models import make_base

asyncio.run(make_base())
PY
```

This will create the `db.sqlite3` file with all required tables.

## Running the bot

Launch the bot with:

```bash
python bot.py
```

The first run will create the database if it does not exist.
