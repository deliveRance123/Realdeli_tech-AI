# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from services.ai import generate_ai_reply


async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers any direct text message using the Gemini AI assistant."""
    if not update.message or not update.message.text:
        return

    # Ignore commands
    if update.message.text.startswith("/"):
        return

    user_text = update.message.text
    user_name = update.effective_user.first_name or "Student/Client"

    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    ai_reply = await generate_ai_reply(user_message=user_text, user_name=user_name)
    await update.message.reply_text(ai_reply)


handlers = [
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text),
]