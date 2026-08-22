import asyncio
import logging
import os
import traceback

from dotenv import load_dotenv
load_dotenv()

from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from database.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").strip().rstrip("/")


async def health_check(request):
    return web.Response(text="RealDeliTechAI Bot is Live and Healthy! ??\n", status=200)


async def webhook_handler(request):
    try:
        data = await request.json()
        tg_app = request.app.get("tg_app")
        if tg_app:
            update = Update.de_json(data, tg_app.bot)
            if update:
                logger.info(f"Incoming webhook update #{update.update_id}")
                await tg_app.process_update(update)
        return web.Response(text="OK", status=200)
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        return web.Response(text="Error", status=500)


async def error_handler(update: object, context) -> None:
    logger.error(f"Telegram Exception handling update: {context.error}\n{traceback.format_exc()}")


async def on_startup(app):
    logger.info("Connecting to database and creating tables...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database init warning: {e}\n{traceback.format_exc()}")

    logger.info("Building Telegram bot application...")
    try:
        tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
        tg_app.add_error_handler(error_handler)

        from handlers import start, orders, topics, ebooks, admin
        for h in start.handlers + orders.handlers + topics.handlers + ebooks.handlers + admin.handlers:
            tg_app.add_handler(h)

        await tg_app.initialize()
        await tg_app.start()
        app["tg_app"] = tg_app

        if WEBHOOK_URL:
            target_url = f"{WEBHOOK_URL}/webhook"
            logger.info(f"Configuring Telegram webhook to: {target_url}")
            await tg_app.bot.set_webhook(url=target_url, drop_pending_updates=False)
            logger.info("Telegram webhook configured successfully!")
        else:
            logger.info("Cleaning up any previous webhooks before starting polling...")
            await tg_app.bot.delete_webhook(drop_pending_updates=False)
            await tg_app.updater.start_polling(drop_pending_updates=False)
            logger.info("Telegram polling started successfully!")

    except Exception as e:
        logger.error(f"Fatal error starting Telegram bot: {e}\n{traceback.format_exc()}")

    logger.info(f"Server is listening on 0.0.0.0:{PORT} - ready for Render health checks.")


async def on_cleanup(app):
    tg_app = app.get("tg_app")
    if tg_app:
        try:
            logger.info("Stopping Telegram bot...")
            if tg_app.updater and tg_app.updater.running:
                await tg_app.updater.stop()
            await tg_app.stop()
            await tg_app.shutdown()
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")


def create_app():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    app.router.add_post("/webhook", webhook_handler)

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


if __name__ == "__main__":
    web_app = create_app()
    web.run_app(web_app, host="0.0.0.0", port=PORT)
