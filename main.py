import asyncio
import logging
import os

from dotenv import load_dotenv
load_dotenv()  # Loads .env file locally; on Render, env vars are already set — safe to call always.

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import init_db
from handlers import start, orders, topics, ebooks

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(orders.router)
    dp.include_router(topics.router)
    dp.include_router(ebooks.router)

    logging.info("RealDeliTechAI bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
