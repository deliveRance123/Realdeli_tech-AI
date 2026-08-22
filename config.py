import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

missing = []
if not BOT_TOKEN:
    missing.append("BOT_TOKEN")
if not DATABASE_URL:
    missing.append("DATABASE_URL")
if not ADMIN_CHAT_ID:
    missing.append("ADMIN_CHAT_ID")

if missing:
    logging.error(f"FATAL: Missing required environment variables: {', '.join(missing)}")
    logging.error("Please add them in Render Dashboard -> Environment tab.")
    sys.exit(1)

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    logging.error(f"FATAL: ADMIN_CHAT_ID must be a numeric integer, got: {ADMIN_CHAT_ID}")
    sys.exit(1)
