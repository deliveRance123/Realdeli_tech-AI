# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4c4 Project Write-up / Seminar Report", callback_data="menu_writeup")],
        [InlineKeyboardButton("\U0001f4a1 Project Topic Suggestion", callback_data="menu_topic")],
        [InlineKeyboardButton("\U0001f3a8 Graphic / Product Design", callback_data="menu_design")],
        [InlineKeyboardButton("\U0001f4da PDFs / Ebooks for Sale", callback_data="menu_ebooks")],
        [InlineKeyboardButton("\U0001f4ac Contact Support / Admin", callback_data="menu_support")],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "\U0001f44b Welcome to <b>RealDeliTechAI</b>!\n\n"
        "We provide professional assistance with:\n"
        "- Project Write-ups & Seminar Reports\n"
        "- Project Topics & Research Guidance\n"
        "- Graphic, UI/UX & Product Design\n"
        "- Academic Guides, PDFs & Ebooks\n\n"
        "Please choose an option below to get started:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "\u2139\ufe0f <b>How to use RealDeliTechAI:</b>\n\n"
        "1. Send /start to open the main service menu.\n"
        "2. Select a service (Write-up, Design, Topics, Ebooks).\n"
        "3. Follow the simple prompts to submit your request.\n"
        "4. You will receive a direct quote and follow-up from our team!\n\n"
        "Send /cancel at any time to return to the main menu."
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "\U0001f4ac <b>Customer Support</b>\n\n"
        "Need instant assistance or have custom inquiries?\n\n"
        "Tap the button below to message our direct support on Telegram."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f468\u200d\U0001f4bb Chat with Admin", url="https://t.me/deliveRance123")],
        [InlineKeyboardButton("\u2b05\ufe0f Back to Menu", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "What do you need today?",
        reply_markup=main_menu_keyboard(),
    )


handlers = [
    CommandHandler("start", cmd_start),
    CommandHandler("help", cmd_help),
    CallbackQueryHandler(show_support, pattern="^menu_support$"),
    CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
]