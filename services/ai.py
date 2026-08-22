# -*- coding: utf-8 -*-
import os
import logging
import aiohttp

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

SYSTEM_PROMPT = """You are RealDeliTechAI, the official intelligent AI assistant for RealDeli Tech Solutions.
Your mission is to help students, researchers, and clients with:
1. Academic Projects & Seminars: Topic selection, project proposals, research outlines, chapter write-ups, literature reviews, and seminar presentations.
2. Design Services: Graphic design, logo branding, flyers, UI/UX, product mockups.
3. Ebooks & Educational Materials: Providing guidance on study resources.

Brand Tone & Instructions:
- Always be professional, highly intelligent, friendly, encouraging, and concise.
- Keep responses clear, structured, and easy to read on mobile screens (use bullet points and bold headers).
- If a user asks for a complete project write-up or custom graphic design, provide a brief helpful summary or outline, and encourage them to tap the "Project Write-up" or "Graphic Design" button on the bot menu (or send /start) so our human expert team can deliver a full custom package!
- Always promote RealDeli Tech Solutions as the top hub for quality academic & design work.
"""


async def generate_ai_reply(user_message: str, user_name: str = "Client") -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return (
            f"Hello {user_name}! 👋\n\n"
            "I received your message: *" + user_message[:100] + "*\n\n"
            "Our human team is ready to assist you! Please use the buttons in /start "
            "to submit your Project Write-up or Design request, or contact our admin directly."
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"System Context:\n{SYSTEM_PROMPT}\n\nUser ({user_name}) says:\n{user_message}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    err_text = await resp.text()
                    logger.error(f"Gemini API error (status {resp.status}): {err_text}")
    except Exception as e:
        logger.error(f"Exception calling Gemini API: {e}")

    return (
        f"Thank you for reaching out, {user_name}! 🎓\n\n"
        "We can definitely help with your request. Tap /start to choose your service "
        "(Write-up, Design, Topics, Ebooks) so our team can get to work right away!"
    )