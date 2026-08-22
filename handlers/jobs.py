# -*- coding: utf-8 -*-
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from services.jobs import fetch_remote_jobs
from services.ai import generate_ai_reply


def jobs_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 All Remote Jobs", callback_data="jobs_cat::all"),
            InlineKeyboardButton("💻 Dev & Tech", callback_data="jobs_cat::dev"),
        ],
        [
            InlineKeyboardButton("🎨 Design & Creative", callback_data="jobs_cat::design"),
            InlineKeyboardButton("✍️ Writing & Content", callback_data="jobs_cat::writing"),
        ],
        [
            InlineKeyboardButton("📊 Marketing & Admin", callback_data="jobs_cat::marketing"),
        ],
        [
            InlineKeyboardButton("📝 AI Proposal Generator", callback_data="job_proposal_help"),
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu"),
        ],
    ])


async def cmd_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💼 <b>RealDeli Remote Job Hunter</b>\n\n"
        "Looking for freelance gigs or remote tech/creative jobs?\n"
        "• Browse 100% free live job listings below.\n"
        "• Use <code>/proposal [Job Details]</code> to get an instant AI cover letter!\n\n"
        "Select a category to browse jobs:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=jobs_menu_keyboard(), parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=jobs_menu_keyboard(), parse_mode="HTML")


async def show_jobs_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.split("::", 1)[1]
    cat_name = category.capitalize()

    await query.edit_message_text(
        f"🔍 <i>Scanning live {cat_name} remote jobs...</i>",
        parse_mode="HTML"
    )

    jobs = await fetch_remote_jobs(category=category, limit=5)

    if not jobs:
        msg = f"No live jobs found right now for <b>{cat_name}</b>. Please check another category!"
    else:
        job_lines = []
        for i, j in enumerate(jobs, 1):
            job_lines.append(
                f"<b>{i}. {j['title']}</b>\n"
                f"🏢 <b>Company:</b> {j['company']}\n"
                f"📍 <b>Location:</b> {j['location']}\n"
                f"🔗 <a href='{j['url']}'>👉 Click to Apply (Free)</a>\n"
            )
        msg = (
            f"💼 <b>Latest {cat_name} Remote Jobs:</b>\n\n" + 
            "\n".join(job_lines) +
            "\n\n💡 <i>Tip: Copy a job title and type <code>/proposal [Job Title]</code> to generate a winning application proposal!</i>"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh / Other Categories", callback_data="menu_jobs")],
        [InlineKeyboardButton("⬅️ Main Menu", callback_data="back_to_menu")],
    ])

    await query.edit_message_text(msg, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


async def show_proposal_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "📝 <b>AI Proposal & Cover Letter Generator</b>\n\n"
        "To generate a custom, winning proposal for any job:\n\n"
        "👉 Type: <code>/proposal [Paste Job Title or Description]</code>\n\n"
        "<b>Example:</b>\n"
        "<code>/proposal Remote Graphic Designer for Social Media Brand</code>\n\n"
        "Our AI will write a professional cover letter ready for you to copy and apply!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Browse Jobs", callback_data="menu_jobs")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")


async def cmd_generate_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_info = " ".join(context.args)
    if not job_info:
        await update.message.reply_text(
            "📝 <b>How to generate a proposal:</b>\n\n"
            "Type <code>/proposal</code> followed by the job title or description.\n\n"
            "<b>Example:</b>\n"
            "<code>/proposal Content Writer for Academic Blog</code>",
            parse_mode="HTML",
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    prompt = (
        f"Write a persuasive, highly professional, concise job proposal / cover letter for the following job opportunity:\n"
        f"'{job_info}'\n\n"
        f"Applicant details: Professional specialist at RealDeli Tech Solutions skilled in high quality delivery, fast turnaround, and excellent communication.\n"
        f"Structure: Enthusiastic greeting, why I am the best fit, relevant skills, call to action. Keep it under 200 words so it's punchy and easy to submit!"
    )

    proposal = await generate_ai_reply(user_message=prompt, user_name=update.effective_user.first_name or "Applicant")

    header = "📝 <b>Your Custom Job Proposal (Ready to Copy & Submit):</b>\n\n"
    await update.message.reply_text(header + proposal)


handlers = [
    CommandHandler(["jobs", "findjobs"], cmd_jobs),
    CommandHandler("proposal", cmd_generate_proposal),
    CallbackQueryHandler(cmd_jobs, pattern="^menu_jobs$"),
    CallbackQueryHandler(show_proposal_help, pattern="^job_proposal_help$"),
    CallbackQueryHandler(show_jobs_category, pattern="^jobs_cat::"),
]