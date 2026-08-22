# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Project Write-up / Seminar Report", callback_data="menu_writeup")],
        [InlineKeyboardButton("💡 Project Topic Suggestion", callback_data="menu_topic")],
        [InlineKeyboardButton("🎨 Graphic / Product Design", callback_data="menu_design")],
        [InlineKeyboardButton("📚 PDFs / Ebooks for Sale", callback_data="menu_ebooks")],
        [InlineKeyboardButton("💼 Find Remote Jobs & Gigs", callback_data="menu_jobs")],
        [InlineKeyboardButton("🤖 Ask RealDeli AI Assistant", callback_data="menu_ask_ai")],
        [InlineKeyboardButton("💬 Contact Support / Admin", callback_data="menu_support")],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome to <b>RealDeliTechAI</b>!\n\n"
        "Your all-in-one hub for:\n"
        "• Project Write-ups & Seminar Reports\n"
        "• Topic Ideas & Academic Research\n"
        "• Graphic, UI/UX & Product Design\n"
        "• Remote Jobs, Freelance Gigs & Ebooks\n"
        "• 24/7 AI Research Assistant\n\n"
        "Please choose an option below or simply type any question to chat with AI:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>How to use RealDeliTechAI:</b>\n\n"
        "1. Send /start to open the main service menu.\n"
        "2. Select a service (Write-up, Design, Topics, Ebooks, Jobs).\n"
        "3. Send /jobs to browse the latest remote job openings.\n"
        "4. Simply type ANY message or question in chat to get an instant AI answer!\n\n"
        "Send /cancel at any time to return to the main menu."
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def show_ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "🤖 <b>RealDeli AI Assistant</b>\n\n"
        "I am trained to help you with academic research, project outlines, "
        "topic generation, and design advice!\n\n"
        "👉 <i>Simply type your question directly in this chat, and I will answer immediately!</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "💬 <b>Customer Support</b>\n\n"
        "Need personal assistance or have custom project inquiries?\n\n"
        "Tap the button below to message our direct support on Telegram."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Chat with Admin", url="https://t.me/deliveRance123")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")],
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
    CallbackQueryHandler(show_ask_ai, pattern="^menu_ask_ai$"),
    CallbackQueryHandler(show_support, pattern="^menu_support$"),
    CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
]