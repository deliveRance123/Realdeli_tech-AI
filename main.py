import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()

from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from database.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").rstrip("/")


async def run_bot():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully.")

    logger.info("Building Telegram Application...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    from handlers import start, orders, topics, ebooks
    for h in start.handlers + orders.handlers + topics.handlers + ebooks.handlers:
        app.add_handler(h)

    await app.initialize()
    await app.start()

    if WEBHOOK_URL:
        logger.info(f"Starting in WEBHOOK mode at {WEBHOOK_URL}/webhook on port {PORT}...")
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            url_path="webhook",
        )
    else:
        logger.info("Starting in POLLING mode...")
        await app.updater.start_polling(drop_pending_updates=True)

    logger.info("RealDeliTechAI bot is now LIVE and running!")
    
    # Run forever until terminated
    stop_signal = asyncio.Event()
    await stop_signal.wait()


def main():
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
