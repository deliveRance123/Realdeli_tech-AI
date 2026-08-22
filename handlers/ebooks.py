from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from sqlalchemy import select

from database.db import async_session
from database.models import Product


async def show_ebooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        text = "No PDFs/ebooks are listed yet. Check back soon!"
    else:
        lines = [f"<b>{p.title}</b> — {p.price}\n{p.description or ''}" for p in products]
        text = "\U0001f4da <b>Available PDFs/Ebooks</b>\n\n" + "\n\n".join(lines)
        text += "\n\nTo buy, just message us the title you want."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("\u2b05\ufe0f Back", callback_data="back_to_menu")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


handlers = [
    CallbackQueryHandler(show_ebooks, pattern="^menu_ebooks$"),
]

