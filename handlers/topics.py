from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler

from data.topics import TOPICS


async def show_departments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = [
        [InlineKeyboardButton(dept, callback_data=f"topic_dept::{dept}")]
        for dept in TOPICS.keys()
    ]
    buttons.append([InlineKeyboardButton("\u2b05\ufe0f Back", callback_data="back_to_menu")])

    await query.edit_message_text(
        "Pick your department:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dept = query.data.split("::", 1)[1]
    topics_list = TOPICS.get(dept, [])

    if not topics_list:
        text = f"No topics loaded yet for <b>{dept}</b> — message us directly and we'll suggest one."
    else:
        lines = "\n".join(f"{i+1}. {t}" for i, t in enumerate(topics_list))
        text = f"<b>{dept} — Suggested Topics</b>\n\n{lines}\n\nWant a custom topic? Tap below."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4c4 Request Write-up for one of these", callback_data="menu_writeup")],
        [InlineKeyboardButton("\u2b05\ufe0f Back", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


handlers = [
    CallbackQueryHandler(show_departments, pattern="^menu_topic$"),
    CallbackQueryHandler(show_topics, pattern="^topic_dept::"),
]

