# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, CommandHandler,
)
from sqlalchemy import select

from database.db import async_session
from database.models import Product
from config import ADMIN_CHAT_ID

WAITING_FOR_RECEIPT = 0


async def start_payment_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("::", 1)[1])
    context.user_data["buying_product_id"] = product_id

    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()

    if not product:
        await query.edit_message_text("Product not found. Please select from /start menu.")
        return ConversationHandler.END

    context.user_data["buying_product_title"] = product.title
    context.user_data["buying_product_price"] = product.price

    msg = (
        f"💳 <b>Purchase: {product.title}</b>\n\n"
        f"💰 <b>Amount:</b> {product.price}\n\n"
        "<b>Payment Instructions:</b>\n"
        "1. Make transfer to our official payment account or link.\n"
        "2. Take a screenshot or receipt proof of your payment.\n"
        "3. <b>Send the receipt image or document directly in this chat!</b>\n\n"
        "Once confirmed, your file will be delivered immediately."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Cancel Payment", callback_data="cancel_payment")]
    ])

    await query.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")
    return WAITING_FOR_RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_title = context.user_data.get("buying_product_title", "PDF Guide")
    product_price = context.user_data.get("buying_product_price", "N/A")
    user = update.effective_user

    await update.message.reply_text(
        "✅ <b>Receipt Received!</b>\n\n"
        "Our admin team is verifying your payment. You will receive your download shortly!",
        parse_mode="HTML"
    )

    admin_caption = (
        f"🧾 <b>New Payment Receipt Proof!</b>\n\n"
        f"<b>Item:</b> {product_title}\n"
        f"<b>Price:</b> {product_price}\n"
        f"<b>Buyer:</b> {user.full_name} (@{user.username or 'no_username'})\n"
        f"<b>Buyer Telegram ID:</b> <code>{user.id}</code>"
    )

    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve & Confirm Delivery", callback_data=f"approve_pay::{user.id}::{product_title}")],
        [InlineKeyboardButton("❌ Decline", callback_data=f"decline_pay::{user.id}")],
    ])

    # Forward photo or document to Admin
    try:
        if update.message.photo:
            photo_file = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_file,
                caption=admin_caption,
                reply_markup=admin_keyboard,
                parse_mode="HTML"
            )
        elif update.message.document:
            doc_file = update.message.document.file_id
            await context.bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=doc_file,
                caption=admin_caption,
                reply_markup=admin_keyboard,
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Error forwarding receipt to admin: {e}")

    return ConversationHandler.END


async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        from handlers.start import main_menu_keyboard
        await query.edit_message_text("Payment cancelled. What do you need today?", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("approve_pay::"):
        parts = data.split("::")
        buyer_id = int(parts[1])
        product_title = parts[2]

        await query.edit_message_caption(
            caption=query.message.caption + "\n\n<b>STATUS: APPROVED ✅</b>",
            parse_mode="HTML"
        )

        try:
            await context.bot.send_message(
                chat_id=buyer_id,
                text=f"🎉 <b>Payment Approved!</b>\n\nYour order for <b>{product_title}</b> has been verified. Our admin is delivering your PDF file in this chat right now!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif data.startswith("decline_pay::"):
        buyer_id = int(data.split("::")[1])
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n<b>STATUS: DECLINED ❌</b>",
            parse_mode="HTML"
        )
        try:
            await context.bot.send_message(
                chat_id=buyer_id,
                text="❌ <b>Payment Verification Issue:</b>\nWe could not verify your receipt. Please contact our support team directly.",
                parse_mode="HTML"
            )
        except Exception:
            pass


payment_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_payment_flow, pattern="^buy_product::"),
    ],
    states={
        WAITING_FOR_RECEIPT: [
            MessageHandler(filters.PHOTO | filters.Document.ALL, receive_receipt),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(cancel_payment, pattern="^cancel_payment$"),
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
)

handlers = [
    payment_conv,
    CallbackQueryHandler(admin_decision, pattern="^(approve_pay|decline_pay)::"),
]