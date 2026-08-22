from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from data.topics import TOPICS

router = Router()


@router.callback_query(F.data == "menu_topic")
async def show_departments(callback: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(text=dept, callback_data=f"topic_dept::{dept}")]
        for dept in TOPICS.keys()
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_menu")])
    await callback.message.edit_text(
        "Pick your department:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topic_dept::"))
async def show_topics(callback: CallbackQuery):
    dept = callback.data.split("::", 1)[1]
    topics = TOPICS.get(dept, [])

    if not topics:
        text = f"No topics loaded yet for *{dept}* — message us directly and we'll suggest one."
    else:
        lines = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics))
        text = f"*{dept} — Suggested Topics*\n\n{lines}\n\nWant a custom topic? Tap below."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Request Write-up for one of these", callback_data="menu_writeup")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_menu")],
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()
