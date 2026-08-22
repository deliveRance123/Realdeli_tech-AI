# -*- coding: utf-8 -*-
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy import select, func

from config import ADMIN_CHAT_ID
from database.db import async_session
from database.models import Customer, Order, Product, Review


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_CHAT_ID


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    async with async_session() as session:
        cust_count = (await session.execute(select(func.count(Customer.id)))).scalar() or 0
        order_count = (await session.execute(select(func.count(Order.id)))).scalar() or 0
        new_orders = (await session.execute(select(func.count(Order.id)).where(Order.status == "new"))).scalar() or 0
        product_count = (await session.execute(select(func.count(Product.id)))).scalar() or 0
        review_count = (await session.execute(select(func.count(Review.id)))).scalar() or 0

    stats_text = (
        "📊 <b>RealDeliTechAI — Admin Command Center</b>\n\n"
        f"👥 <b>Total Customers Registered:</b> {cust_count}\n"
        f"📦 <b>Total Orders:</b> {order_count}\n"
        f"🆕 <b>Pending Orders:</b> {new_orders}\n"
        f"📚 <b>Listed Products:</b> {product_count}\n"
        f"⭐ <b>Client Reviews:</b> {review_count}\n\n"
        "<b>Admin Commands:</b>\n"
        "• /orders — View recent 5 orders\n"
        "• /addproduct Title | Price | Description — Add PDF/Ebook\n"
        "• /broadcast [Message] — Send announcement to ALL customers"
    )
    await update.message.reply_text(stats_text, parse_mode="HTML")


async def cmd_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    async with async_session() as session:
        result = await session.execute(
            select(Order).order_by(Order.id.desc()).limit(5)
        )
        orders = result.scalars().all()

    if not orders:
        await update.message.reply_text("No orders placed yet.")
        return

    lines = []
    for o in orders:
        lines.append(
            f"<b>Order #{o.id}</b> [{o.status.upper()}]\n"
            f"Category: {o.category}\n"
            f"Details: {o.details[:120]}..."
        )

    await update.message.reply_text(
        "📦 <b>Recent Orders:</b>\n\n" + "\n\n".join(lines),
        parse_mode="HTML",
    )


async def cmd_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = " ".join(context.args)
    if not text or "|" not in text:
        await update.message.reply_text(
            "<b>Usage:</b>\n<code>/addproduct Title | Price | Description</code>\n\n"
            "<b>Example:</b>\n<code>/addproduct AI Research Guide | ₦2,500 | Complete PDF guide on modern AI research.</code>",
            parse_mode="HTML",
        )
        return

    parts = [p.strip() for p in text.split("|")]
    title = parts[0]
    price = parts[1] if len(parts) > 1 else "Contact for price"
    desc = parts[2] if len(parts) > 2 else ""

    async with async_session() as session:
        product = Product(title=title, price=price, description=desc)
        session.add(product)
        await session.commit()

    await update.message.reply_text(
        f"✅ <b>Product Added!</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Price:</b> {price}\n"
        f"<b>Description:</b> {desc}",
        parse_mode="HTML",
    )


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcasts a promotional announcement to all registered bot users."""
    if not is_admin(update.effective_user.id):
        return

    broadcast_msg = " ".join(context.args)
    if not broadcast_msg:
        await update.message.reply_text(
            "📢 <b>Mass Broadcast Tool:</b>\n\n"
            "Type <code>/broadcast [Your Message]</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/broadcast 🎓 Promo Alert! 20% discount on all project write-ups this week! Tap /start to book.</code>",
            parse_mode="HTML"
        )
        return

    async with async_session() as session:
        result = await session.execute(select(Customer.telegram_id))
        user_ids = [r[0] for r in result.fetchall()]

    if not user_ids:
        await update.message.reply_text("No customers registered in the database yet.")
        return

    await update.message.reply_text(f"🚀 <i>Broadcasting message to {len(user_ids)} users...</i>", parse_mode="HTML")

    success_count = 0
    fail_count = 0

    formatted_msg = (
        "📢 <b>Announcement from RealDeli Tech Solutions</b>\n\n" +
        broadcast_msg +
        "\n\n👉 <i>Tap /start to explore our services!</i>"
    )

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=formatted_msg, parse_mode="HTML")
            success_count += 1
            await asyncio.sleep(0.05)  # Rate limit prevention
        except Exception:
            fail_count += 1

    await update.message.reply_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"• Delivered to: <b>{success_count}</b> customers\n"
        f"• Failed/Blocked: <b>{fail_count}</b>",
        parse_mode="HTML"
    )


handlers = [
    CommandHandler(["admin", "stats"], cmd_stats),
    CommandHandler("orders", cmd_orders),
    CommandHandler("addproduct", cmd_add_product),
    CommandHandler("broadcast", cmd_broadcast),
]