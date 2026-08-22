from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from config import ADMIN_CHAT_ID
from database.db import async_session
from database.models import Customer, Order

router = Router()

CATEGORY_LABELS = {
    "menu_writeup": ("write_up", "Project Write-up / Seminar Report"),
    "menu_design": ("design", "Graphic / Product Design"),
}


class OrderForm(StatesGroup):
    waiting_for_details = State()


@router.callback_query(F.data.in_(CATEGORY_LABELS.keys()))
async def start_order(callback: CallbackQuery, state: FSMContext):
    category_key, label = CATEGORY_LABELS[callback.data]
    await state.update_data(category=category_key, category_label=label)
    await state.set_state(OrderForm.waiting_for_details)

    if category_key == "write_up":
        prompt = (
            f"*{label}*\n\n"
            "Please send me the following in one message:\n"
            "1. Your name\n"
            "2. School / Department\n"
            "3. Project topic (or 'need a topic')\n"
            "4. Deadline\n"
            "5. Any extra notes"
        )
    else:
        prompt = (
            f"*{label}*\n\n"
            "Please send me the following in one message:\n"
            "1. Your name\n"
            "2. What you need designed (flyer, logo, mockup, etc.)\n"
            "3. Size/format if known\n"
            "4. Deadline\n"
            "5. Reference images/links (if any)"
        )

    await callback.message.edit_text(prompt, parse_mode="Markdown")
    await callback.answer()


@router.message(OrderForm.waiting_for_details)
async def receive_order_details(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data["category"]
    category_label = data["category_label"]

    async with async_session() as session:
        result = await session.execute(
            select(Customer).where(Customer.telegram_id == message.from_user.id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            customer = Customer(
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
                username=message.from_user.username,
            )
            session.add(customer)
            await session.flush()

        order = Order(
            customer_id=customer.id,
            category=category,
            details=message.text,
            status="new",
        )
        session.add(order)
        await session.commit()
        order_id = order.id

    await message.answer(
        "✅ Got it! Your request has been sent. I'll DM you a quote shortly."
    )

    admin_text = (
        f"🆕 *New {category_label} Request* (Order #{order_id})\n\n"
        f"From: {message.from_user.full_name} (@{message.from_user.username or 'no_username'})\n"
        f"Telegram ID: {message.from_user.id}\n\n"
        f"Details:\n{message.text}"
    )
    await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="Markdown")

    await state.clear()
