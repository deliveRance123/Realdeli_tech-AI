import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()  # Loads .env locally; on Render, env vars are already set.

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, orders, topics, ebooks

logging.basicConfig(level=logging.INFO)

# Render sets PORT automatically. WEBHOOK_URL = your Render service public URL.
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PATH = "/webhook"


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(orders.router)
    dp.include_router(topics.router)
    dp.include_router(ebooks.router)

    # Tell Telegram where to send updates
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logging.info(f"Webhook set: {WEBHOOK_URL}{WEBHOOK_PATH}")

    # Build the web app that receives Telegram updates
    app = web.Application()

    # Health check so Render knows the service is alive
    async def health(request):
        return web.Response(text="RealDeliTechAI bot is running OK")

    app.router.add_get("/", health)

    # Wire aiogram into the web server
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logging.info(f"Bot running on port {PORT}")
    await asyncio.Event().wait()  # Keep running forever


if __name__ == "__main__":
    asyncio.run(main())

