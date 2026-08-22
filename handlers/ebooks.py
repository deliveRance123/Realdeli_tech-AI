# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from sqlalchemy import select

from database.db import async_session
from database.models import Product


async def show_ebooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

    buttons = []
    if not products:
        text = (
            "📚 <b>RealDeli Academic Guides & Ebooks</b>\n\n"
            "We have comprehensive PDF materials available:\n\n"
            "1. <b>Undergraduate Final Year Research Masterclass</b> — ₦2,500\n"
            "   <i>Complete guide on Proposal, Chapter 1-5, and Oral Defense.</i>\n\n"
            "2. <b>AI Tools for Fast Seminar & Thesis Writing</b> — ₦2,000\n"
            "   <i>How to use modern AI to research faster without plagiarism.</i>\n\n"
            "To purchase, select an option below or message our admin directly!"
        )
        buttons.append([InlineKeyboardButton("💬 Order via Admin DM", url="https://t.me/deliveRance123")])
    else:
        lines = []
        for p in products:
            lines.append(f"• <b>{p.title}</b> — <b>{p.price}</b>\n  <i>{p.description or ''}</i>")
            buttons.append([InlineKeyboardButton(f"💳 Buy {p.title[:20]} ({p.price})", callback_data=f"buy_product::{p.id}")])
        text = "📚 <b>Available PDFs & Research Materials:</b>\n\n" + "\n\n".join(lines)

    buttons.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")])
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


handlers = [
    CallbackQueryHandler(show_ebooks, pattern="^menu_ebooks$"),
]