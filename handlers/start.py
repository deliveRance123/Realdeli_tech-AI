# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Project / Seminar Write-up", callback_data="menu_writeup"),
            InlineKeyboardButton("🎨 Graphic & UI Design", callback_data="menu_design"),
        ],
        [
            InlineKeyboardButton("🎓 AI Academic Toolkit", callback_data="menu_academic"),
            InlineKeyboardButton("💡 Project Topics Bank", callback_data="menu_topic"),
        ],
        [
            InlineKeyboardButton("📚 PDFs & Ebooks for Sale", callback_data="menu_ebooks"),
            InlineKeyboardButton("💼 Find Remote Jobs", callback_data="menu_jobs"),
        ],
        [
            InlineKeyboardButton("⭐ Client Reviews & Proof", callback_data="menu_reviews"),
            InlineKeyboardButton("🤖 Ask RealDeli AI", callback_data="menu_ask_ai"),
        ],
        [
            InlineKeyboardButton("💬 Contact Support / Admin", callback_data="menu_support"),
        ],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Welcome to <b>RealDeliTechAI</b>!\n\n"
        "Your all-in-one platform for:\n"
        "• Academic Project & Seminar Write-ups\n"
        "• Graphic, UI/UX & Brand Design\n"
        "• AI Research Toolkit (/outline, /paraphrase, /cite)\n"
        "• Remote Jobs & Freelance Leads (/jobs)\n"
        "• 24/7 AI Research Assistant\n\n"
        "Please choose a service below or type any question to chat with AI:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>How to use RealDeliTechAI:</b>\n\n"
        "1. Send /start to open the full service menu.\n"
        "2. Send /academic for AI outlines, paraphrasing & citations.\n"
        "3. Send /jobs to browse verified remote freelance jobs.\n"
        "4. Send /proposal [Job Title] to generate a winning cover letter.\n"
        "5. Send /reviews to see verified client feedback.\n"
        "6. Type ANY question in this chat for instant AI help!\n\n"
        "Send /cancel at any time to return to the main menu."
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def show_ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "🤖 <b>RealDeli AI Assistant</b>\n\n"
        "I am trained to help you with research questions, project ideas, "
        "topic outlines, and design advice!\n\n"
        "👉 <i>Simply type your question directly in this chat, and I will reply immediately!</i>"
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
        "Need personal assistance or have custom project requirements?\n\n"
        "Tap below to chat directly with our lead consultant."
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