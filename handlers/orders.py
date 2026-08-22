from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, CommandHandler,
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
            "Please reply with the following details in one message:\n\n"
            "1. Your Full Name\n"
            "2. School / Department / Level\n"
            "3. Project Topic (or specify 'Need Topic Suggestion')\n"
            "4. Deadline Date\n"
            "5. Any Specific Requirements / Notes"
        )
    else:
        prompt = (
            f"<b>{label}</b>\n\n"
            "Please reply with the following details in one message:\n\n"
            "1. Your Full Name\n"
            "2. Design Type (Flyer, Logo, UI Mockup, Banner, etc.)\n"
            "3. Format / Dimensions (if known)\n"
            "4. Deadline Date\n"
            "5. Reference Links or Style Preferences"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("\u2b05\ufe0f Cancel & Return to Menu", callback_data="cancel_order")]
    ])
    await query.edit_message_text(prompt, reply_markup=keyboard, parse_mode="HTML")
    return WAITING_FOR_DETAILS


async def receive_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.user_data.get("category", "general")
    category_label = context.user_data.get("category_label", "Service")

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

    success_msg = (
        "\u2705 <b>Request Received Successfully!</b>\n\n"
        f"Your Order ID is: <code>#{order_id}</code>\n"
        "Our team has been notified and will contact you with a quote and delivery timeline."
    )
    await update.message.reply_text(success_msg, parse_mode="HTML")

    # Notify Admin immediately
    admin_text = (
        f"\U0001f195 <b>New {category_label} Request</b> (Order #{order_id})\n\n"
        f"<b>Customer:</b> {update.effective_user.full_name}\n"
        f"<b>Username:</b> @{update.effective_user.username or 'No username'}\n"
        f"<b>Telegram ID:</b> <code>{update.effective_user.id}</code>\n\n"
        f"<b>Details:</b>\n{update.message.text}"
    )
    try:
        await context.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending admin notification: {e}")

    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        from handlers.start import main_menu_keyboard
        await query.edit_message_text(
            "Request cancelled. What do you need today?",
            reply_markup=main_menu_keyboard(),
        )
    return ConversationHandler.END


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.start import main_menu_keyboard
    await update.message.reply_text(
        "Operation cancelled. Main menu:",
        reply_markup=main_menu_keyboard(),
    )
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
        CallbackQueryHandler(cancel_order, pattern="^(cancel_order|back_to_menu)$"),
        CommandHandler("cancel", cancel_cmd),
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
)

handlers = [_conv]
