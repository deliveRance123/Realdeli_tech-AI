# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.ai import generate_ai_reply


def academic_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Project Outline Builder", callback_data="acad_help::outline"),
            InlineKeyboardButton("✍️ Plagiarism Paraphraser", callback_data="acad_help::paraphrase"),
        ],
        [
            InlineKeyboardButton("📖 Citation & Reference Tool", callback_data="acad_help::cite"),
        ],
        [
            InlineKeyboardButton("📄 Request Full Project Write-up", callback_data="menu_writeup"),
        ],
        [
            InlineKeyboardButton("⬅️ Main Menu", callback_data="back_to_menu"),
        ],
    ])


async def cmd_academic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎓 <b>RealDeli AI Academic Toolkit</b>\n\n"
        "Supercharge your school project and research with our instant AI tools:\n\n"
        "• <b>/outline [Topic]</b> — Generates a complete 5-Chapter project breakdown.\n"
        "• <b>/paraphrase [Text]</b> — Rewrites text into academic language to eliminate plagiarism.\n"
        "• <b>/cite [Book/Paper Info]</b> — Generates instant APA 7th & Harvard citations.\n\n"
        "Select a tool below or type a command to get started:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=academic_menu_keyboard(), parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=academic_menu_keyboard(), parse_mode="HTML")


async def show_academic_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tool = query.data.split("::", 1)[1]
    if tool == "outline":
        msg = (
            "📋 <b>Project Proposal & Outline Builder</b>\n\n"
            "Generate a complete 5-chapter project outline with problem statement, objectives & methodology.\n\n"
            "👉 <b>Usage:</b>\n"
            "<code>/outline Web-Based Cargo Tracking System</code>\n"
            "<code>/outline Impact of Digital Marketing on Small Businesses</code>"
        )
    elif tool == "paraphrase":
        msg = (
            "✍️ <b>Plagiarism Paraphraser</b>\n\n"
            "Rewrite literature reviews and paragraphs to be 100% plagiarism-free while maintaining scholarly tone.\n\n"
            "👉 <b>Usage:</b>\n"
            "<code>/paraphrase [Paste your text here]</code>"
        )
    else:
        msg = (
            "📖 <b>Academic Citation Generator</b>\n\n"
            "Generate properly formatted APA 7th and Harvard reference citations.\n\n"
            "👉 <b>Usage:</b>\n"
            "<code>/cite Title, Author, Year</code>\n"
            "<i>Example:</i> <code>/cite Clean Code by Robert C. Martin 2008</code>"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎓 Back to Academic Menu", callback_data="menu_academic")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML")


async def cmd_outline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text(
            "📋 <b>How to use:</b>\nType <code>/outline [Your Topic]</code>\n\n"
            "<b>Example:</b>\n<code>/outline AI-Powered Attendance Management System</code>",
            parse_mode="HTML",
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = (
        f"Generate a rigorous, professional 5-Chapter academic project proposal outline for the topic:\n"
        f"'{topic}'\n\n"
        f"Structure required:\n"
        f"Chapter 1: Background, Problem Statement, 3 Specific Objectives, Significance\n"
        f"Chapter 2: Conceptual & Theoretical Framework, Empirical Literature Themes\n"
        f"Chapter 3: Methodology (Design, Data Collection/Tools, Analysis Technique/Architecture)\n"
        f"Chapter 4: Implementation Strategy / System Modules\n"
        f"Chapter 5: Summary & Expected Contribution\n"
        f"Keep it concise, clear, and structured for an undergraduate/postgraduate student."
    )

    result = await generate_ai_reply(user_message=prompt, user_name=update.effective_user.first_name or "Student")

    header = f"📋 <b>Academic Project Outline for:</b>\n<i>{topic}</i>\n\n"
    footer = "\n\n💡 <i>Need our team to write the full project for you? Tap /start -> 'Project Write-up'!</i>"
    await update.message.reply_text(header + result + footer, parse_mode="HTML")


async def cmd_paraphrase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_to_paraphrase = " ".join(context.args)
    if not text_to_paraphrase:
        await update.message.reply_text(
            "✍️ <b>How to use:</b>\nType <code>/paraphrase [Paste text to rewrite]</code>",
            parse_mode="HTML",
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = (
        f"Paraphrase the following academic passage into clear, scholarly, plagiarism-free English. "
        f"Provide 2 alternative academic versions (Version 1: Standard Academic, Version 2: Advanced Scholarly):\n\n"
        f"{text_to_paraphrase}"
    )

    result = await generate_ai_reply(user_message=prompt, user_name=update.effective_user.first_name or "Researcher")
    await update.message.reply_text(f"✍️ <b>Paraphrased Academic Versions:</b>\n\n{result}", parse_mode="HTML")


async def cmd_cite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source_info = " ".join(context.args)
    if not source_info:
        await update.message.reply_text(
            "📖 <b>How to use:</b>\nType <code>/cite [Author, Title, Year, Publisher/Journal]</code>\n\n"
            "<b>Example:</b>\n<code>/cite Goodfellow, Deep Learning, 2016, MIT Press</code>",
            parse_mode="HTML",
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = (
        f"Format standard reference citations for the following academic work in 3 formats (APA 7th Edition, Harvard Style, MLA 9th):\n"
        f"{source_info}\n\n"
        f"Include in-text citation examples for each."
    )

    result = await generate_ai_reply(user_message=prompt, user_name=update.effective_user.first_name or "Scholar")
    await update.message.reply_text(f"📖 <b>Formatted Citations:</b>\n\n{result}", parse_mode="HTML")


handlers = [
    CommandHandler(["academic", "toolkit"], cmd_academic),
    CommandHandler("outline", cmd_outline),
    CommandHandler(["paraphrase", "rewrite"], cmd_paraphrase),
    CommandHandler("cite", cmd_cite),
    CallbackQueryHandler(cmd_academic, pattern="^menu_academic$"),
    CallbackQueryHandler(show_academic_help, pattern="^acad_help::"),
]