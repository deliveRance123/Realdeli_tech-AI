from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy import select, func

from config import ADMIN_CHAT_ID
from database.db import async_session
from database.models import Customer, Order, Product


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

    stats_text = (
        "\U0001f4ca <b>RealDeliTechAI — Admin Dashboard</b>\n\n"
        f"\U0001f465 <b>Total Customers:</b> {cust_count}\n"
        f"\U0001f4e6 <b>Total Orders:</b> {order_count}\n"
        f"\U0001f195 <b>Pending Orders:</b> {new_orders}\n"
        f"\U0001f4da <b>Listed Products:</b> {product_count}\n\n"
        "<b>Admin Commands:</b>\n"
        "• /orders — View recent 5 orders\n"
        "• /addproduct Title | Price | Description — Add PDF/Ebook"
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
        "\U0001f4e6 <b>Recent Orders:</b>\n\n" + "\n\n".join(lines),
        parse_mode="HTML",
    )


async def cmd_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = " ".join(context.args)
    if not text or "|" not in text:
        await update.message.reply_text(
            "<b>Usage:</b>\n<code>/addproduct Title | Price | Description</code>\n\n"
            "<b>Example:</b>\n<code>/addproduct AI Research Guide | ?2,500 | Complete PDF guide on modern AI research.</code>",
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
        f"\u2705 <b>Product Added!</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Price:</b> {price}\n"
        f"<b>Description:</b> {desc}",
        parse_mode="HTML",
    )


handlers = [
    CommandHandler(["admin", "stats"], cmd_stats),
    CommandHandler("orders", cmd_orders),
    CommandHandler("addproduct", cmd_add_product),
]
