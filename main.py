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
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")


def main():
    async def post_init(application):
        await init_db()
        logger.info("Database initialized")

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    from handlers import start, orders, topics, ebooks
    for h in start.handlers + orders.handlers + topics.handlers + ebooks.handlers:
        app.add_handler(h)

    logger.info("RealDeliTechAI bot starting...")

    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            url_path="webhook",
        )
    else:
        app.run_polling()


if __name__ == "__main__":
    main()
