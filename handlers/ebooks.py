from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from database.db import async_session
from database.models import Product

router = Router()


@router.callback_query(F.data == "menu_ebooks")
async def show_ebooks(callback: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    if not products:
        text = "No PDFs/ebooks are listed yet. Check back soon!"
    else:
        lines = []
        for p in products:
            lines.append(f"<b>{p.title}</b> — {p.price}\n{p.description or ''}")
        text = "📚 <b>Available PDFs/Ebooks</b>\n\n" + "\n\n".join(lines)
        text += "\n\nTo buy, just message us the title you want."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()
