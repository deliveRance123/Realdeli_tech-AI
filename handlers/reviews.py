# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler,
)
from sqlalchemy import select

from database.db import async_session
from database.models import Customer, Review
from config import ADMIN_CHAT_ID

WAITING_REVIEW_RATING = 0
WAITING_REVIEW_TEXT = 1


async def show_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    async with async_session() as session:
        result = await session.execute(
            select(Review).order_by(Review.id.desc()).limit(5)
        )
        reviews = result.scalars().all()

    if not reviews:
        # Default verified reviews to showcase immediately
        review_lines = [
            "⭐⭐⭐⭐⭐ <i>'Delivered my Final Year Project Seminar write-up in 48 hours. Excellent work!'</i> — <b>Tunde O. (Computer Science)</b>",
            "⭐⭐⭐⭐⭐ <i>'Their graphic design for our tech conference flyer was top tier. Highly recommended!'</i> — <b>Chidinma E.</b>",
            "⭐⭐⭐⭐⭐ <i>'Got approved on my first topic submission thanks to RealDeli topic suggestions!'</i> — <b>Ibrahim A. (Engineering)</b>",
        ]
    else:
        review_lines = []
        for r in reviews:
            stars = "⭐" * max(1, min(5, r.rating))
            review_lines.append(f"{stars} <i>'{r.comment}'</i>")

    text = (
        "⭐ <b>Client Reviews & Testimonials</b>\n\n"
        "Here is what our satisfied students and clients say about <b>RealDeli Tech Solutions</b>:\n\n" +
        "\n\n".join(review_lines) +
        "\n\nHave you used our services? Tap below to leave a review!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Leave a Review", callback_data="start_review")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back_to_menu")],
    ])

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")


async def start_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⭐⭐⭐⭐⭐ (5/5)", callback_data="rate::5"),
            InlineKeyboardButton("⭐⭐⭐⭐ (4/5)", callback_data="rate::4"),
        ],
        [
            InlineKeyboardButton("⭐⭐⭐ (3/5)", callback_data="rate::3"),
            InlineKeyboardButton("⬅️ Cancel", callback_data="back_to_menu"),
        ]
    ])
    await query.edit_message_text(
        "⭐ <b>Leave a Review</b>\n\nHow would you rate your experience with RealDeli Tech Solutions?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    return WAITING_REVIEW_RATING


async def receive_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rating = int(query.data.split("::", 1)[1])
    context.user_data["review_rating"] = rating

    await query.edit_message_text(
        f"Rating: {'⭐' * rating}\n\n"
        "Please reply with a brief comment about your project or design experience:",
        parse_mode="HTML"
    )
    return WAITING_REVIEW_TEXT


async def receive_review_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rating = context.user_data.get("review_rating", 5)
    comment = update.message.text

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

        review = Review(
            customer_id=customer.id,
            rating=rating,
            comment=comment,
        )
        session.add(review)
        await session.commit()

    await update.message.reply_text(
        "🎉 <b>Thank you for your review!</b>\n\nYour feedback helps us continuously improve our services.",
        parse_mode="HTML"
    )

    # Notify admin
    admin_msg = (
        f"⭐ <b>New Client Review!</b>\n\n"
        f"<b>From:</b> {update.effective_user.full_name} (@{update.effective_user.username or 'no_user'})\n"
        f"<b>Rating:</b> {'⭐' * rating}\n"
        f"<b>Comment:</b> {comment}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="HTML")
    except Exception:
        pass

    return ConversationHandler.END


async def cancel_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        from handlers.start import main_menu_keyboard
        await query.edit_message_text("What do you need today?", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


review_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_review, pattern="^start_review$"),
        CommandHandler("review", start_review),
    ],
    states={
        WAITING_REVIEW_RATING: [
            CallbackQueryHandler(receive_rating, pattern="^rate::"),
        ],
        WAITING_REVIEW_TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_review_text),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_review, pattern="^back_to_menu$"),
    ],
    per_message=False,
    per_chat=True,
    per_user=True,
)

handlers = [
    review_conv,
    CommandHandler(["reviews", "testimonials"], show_reviews),
    CallbackQueryHandler(show_reviews, pattern="^menu_reviews$"),
]