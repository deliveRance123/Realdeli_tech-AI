from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4c4 Project Write-up / Seminar Report", callback_data="menu_writeup")],
        [InlineKeyboardButton("\U0001f4a1 Project Topic Suggestion", callback_data="menu_topic")],
        [InlineKeyboardButton("\U0001f3a8 Graphic / Product Design", callback_data="menu_design")],
        [InlineKeyboardButton("\U0001f4da PDFs / Ebooks for Sale", callback_data="menu_ebooks")],
    ])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "\U0001f44b Welcome to <b>RealDeliTechAI</b>.\n\n"
        "We help students with project write-ups, seminar reports, "
        "topic suggestions, and graphic/product design.\n\n"
        "What do you need today?"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("What do you need today?", reply_markup=main_menu_keyboard())


handlers = [
    CommandHandler("start", cmd_start),
    CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
]

