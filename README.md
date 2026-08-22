# RealDeliTechAI — Telegram Bot

A Telegram bot for RealdeliTech Solutions that takes in:
- Project write-up / seminar report requests
- Project topic suggestions (per department)
- Graphic/product design requests
- PDF/ebook sales listing

Every request gets DM'd straight to your personal Telegram chat, and saved
in a PostgreSQL database.

## 1. Get your bot token (free, already done)
You already have this from @BotFather. Keep it secret — don't post it
publicly or commit it to GitHub.

## 2. Get your admin chat ID (free)
Message **@userinfobot** on Telegram — it replies with your numeric ID.
This is where all new orders will be sent.

## 3. Free PostgreSQL database
Two good free options:
- **Render Postgres** (free tier, expires after 90 days but easy to recreate)
- **Supabase** (free tier, no expiry, recommended for a longer-term free option)

Either way, you'll get a connection string that looks like:
```
postgresql://user:password@host:5432/dbname
```
That's your `DATABASE_URL`.

## 4. Deploy on Render (free)

1. Push this project folder to a GitHub repository (create one at github.com,
   free).
2. Go to render.com → New → **Background Worker** (not Web Service, since
   this bot uses polling, not a webhook).
3. Connect your GitHub repo.
4. Build command: `pip install -r requirements.txt`
5. Start command: `python main.py`
6. Under **Environment**, add these three variables:
   - `BOT_TOKEN` = your token from BotFather
   - `DATABASE_URL` = your Postgres connection string from step 3
   - `ADMIN_CHAT_ID` = your numeric ID from step 2
7. Deploy. Render will install dependencies and start the bot automatically.

Render's free background worker tier does have limited free hours per month —
enough to run a low-traffic bot continuously in most cases, but check
Render's current free-tier limits since they do change.

## 5. Test it
Open your bot on Telegram (the @username you set with BotFather), send
`/start`, and walk through the menu. New orders should appear in your DM
(the ADMIN_CHAT_ID chat) within seconds.

## 6. Adding real project topics
Edit `data/topics.py` — add your department and a list of 5+ topics.
This is plain Python, no database needed for this part.

## 7. Adding ebooks/PDFs for sale
Right now the ebook menu reads from a `products` database table, which
starts empty. To add a product, connect to your Postgres database (e.g. via
Supabase's table editor, or a quick Python script) and insert a row with a
title, description, and price. A simple admin command to add products
directly from Telegram can be added later once you're getting real traffic.

## What this version does NOT do (be aware)
- No payment integration yet — you confirm payment manually before
  delivering. Add Paystack once you have steady orders.
- No automatic group scouting — Telegram doesn't allow bots to search and
  join groups on their own. If you want group monitoring, you must add the
  bot manually to groups you're already a member of.
