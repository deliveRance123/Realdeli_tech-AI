from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Project Write-up / Seminar Report", callback_data="menu_writeup")],
        [InlineKeyboardButton(text="💡 Project Topic Suggestion", callback_data="menu_topic")],
        [InlineKeyboardButton(text="🎨 Graphic / Product Design", callback_data="menu_design")],
        [InlineKeyboardButton(text="📚 PDFs / Ebooks for Sale", callback_data="menu_ebooks")],
    ])


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "👋 Welcome to *RealDeliTechAI*.\n\n"
        "We help students with project write-ups, seminar reports, "
        "topic suggestions, and graphic/product design.\n\n"
        "What do you need today?"
    )
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "What do you need today?",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
