import os

# These come from environment variables — never hardcode them in the code.
# On Render, you set these in the "Environment" tab of your service.

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# Your personal Telegram numeric chat ID — this is where the bot sends
# every new order/design request so you see it in your own DM.
# How to get it: message @userinfobot on Telegram, it replies with your ID.
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")
if not ADMIN_CHAT_ID:
    raise RuntimeError("ADMIN_CHAT_ID environment variable is not set")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
