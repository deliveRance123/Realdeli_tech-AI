import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from database.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")


async def post_init(application):
    await init_db()
    logger.info("Database initialized successfully")


def main():
    # Fix for Python 3.12+ / 3.14 where get_event_loop no longer creates a loop automatically
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    from handlers import start, orders, topics, ebooks
    for h in start.handlers + orders.handlers + topics.handlers + ebooks.handlers:
        app.add_handler(h)

    logger.info("RealDeliTechAI bot starting...")

    if WEBHOOK_URL:
        logger.info(f"Running in WEBHOOK mode at {WEBHOOK_URL}/webhook on port {PORT}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            url_path="webhook",
        )
    else:
        logger.info("Running in POLLING mode...")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
