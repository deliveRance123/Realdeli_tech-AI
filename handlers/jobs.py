# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.jobs import fetch_remote_jobs


def jobs_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 All Remote Jobs", callback_data="jobs_cat::all"),
            InlineKeyboardButton("💻 Dev & Tech", callback_data="jobs_cat::dev"),
        ],
        [
            InlineKeyboardButton("🎨 Design & Creative", callback_data="jobs_cat::design"),
            InlineKeyboardButton("✍️ Writing & Content", callback_data="jobs_cat::writing"),
        ],
        [
            InlineKeyboardButton("📊 Marketing & Admin", callback_data="jobs_cat::marketing"),
        ],
        [
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu"),
        ],
    ])


async def cmd_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💼 <b>RealDeli Remote Job Hunter</b>\n\n"
        "Looking for freelance gigs or remote tech/creative jobs?\n"
        "Select a category below to browse the latest live job postings:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=jobs_menu_keyboard(), parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=jobs_menu_keyboard(), parse_mode="HTML")


async def show_jobs_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.split("::", 1)[1]
    cat_name = category.capitalize()

    await query.edit_message_text(
        f"🔍 <i>Searching latest {cat_name} remote jobs...</i>",
        parse_mode="HTML"
    )

    jobs = await fetch_remote_jobs(category=category, limit=5)

    if not jobs:
        msg = f"No live jobs found right now for <b>{cat_name}</b>. Please check another category!"
    else:
        job_lines = []
        for i, j in enumerate(jobs, 1):
            job_lines.append(
                f"<b>{i}. {j['title']}</b>\n"
                f"🏢 <b>Company:</b> {j['company']}\n"
                f"📍 <b>Location:</b> {j['location']}\n"
                f"🔗 <a href='{j['url']}'>👉 Click to Apply</a>\n"
            )
        msg = f"💼 <b>Latest {cat_name} Remote Jobs:</b>\n\n" + "\n".join(job_lines)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh / Other Categories", callback_data="menu_jobs")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back_to_menu")],
    ])

    await query.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


handlers = [
    CommandHandler(["jobs", "findjobs"], cmd_jobs),
    CallbackQueryHandler(cmd_jobs, pattern="^menu_jobs$"),
    CallbackQueryHandler(show_jobs_category, pattern="^jobs_cat::"),
]