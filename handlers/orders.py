from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler,
)
from sqlalchemy import select

from config import ADMIN_CHAT_ID
from database.db import async_session
from database.models import Customer, Order

WAITING_FOR_DETAILS = 0

CATEGORY_LABELS = {
    "menu_writeup": ("write_up", "Project Write-up / Seminar Report"),
    "menu_design": ("design", "Graphic / Product Design"),
}


async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_key, label = CATEGORY_LABELS[query.data]
    context.user_data["category"] = category_key
    context.user_data["category_label"] = label

    if category_key == "write_up":
        prompt = (
            f"<b>{label}</b>\n\n"
            "Please send me the following in one message:\n"
            "1. Your name\n"
            "2. School / Department\n"
            "3. Project topic (or 'need a topic')\n"
            "4. Deadline\n"
            "5. Any extra notes"
        )
    else:
        prompt = (
            f"<b>{label}</b>\n\n"
            "Please send me the following in one message:\n"
            "1. Your name\n"
            "2. What you need designed (flyer, logo, mockup, etc.)\n"
            "3. Size/format if known\n"
            "4. Deadline\n"
            "5. Reference images/links (if any)"
        )

    await query.edit_message_text(prompt, parse_mode="HTML")
    return WAITING_FOR_DETAILS


async def receive_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data.get("category")
    category_label = context.user_data.get("category_label")

    async with async_session() as session:
        result = await session.execute(
            select(Customer).where(Customer.telegram_id == update.effective_user.id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            customer = Customer(
                telegram_id=update.effective_user.id,
                name=update.effective_user.full_name,
                username=update.effective_user.username,
            )
            session.add(customer)
            await session.flush()

        order = Order(
            customer_id=customer.id,
            category=category,
            details=update.message.text,
            status="new",
        )
        session.add(order)
        await session.commit()
        order_id = order.id

    await update.message.reply_text(
        "\u2705 Got it! Your request has been sent. I'll DM you a quote shortly."
    )

    admin_text = (
        f"\U0001f195 <b>New {category_label} Request</b> (Order #{order_id})\n\n"
        f"From: {update.effective_user.full_name} "
        f"(@{update.effective_user.username or 'no_username'})\n"
        f"Telegram ID: {update.effective_user.id}\n\n"
        f"Details:\n{update.message.text}"
    )
    await context.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")

    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
    return ConversationHandler.END


_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_order, pattern="^(menu_writeup|menu_design)$")
    ],
    states={
        WAITING_FOR_DETAILS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_order_details)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_order, pattern="^back_to_menu$")
    ],
    per_message=False,
)

handlers = [_conv]

