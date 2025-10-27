import re
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ✅ Token setup
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "7864547833:AAFc-opzjNY_hMYTZzpCF4STfNwO6zRnUFw"

# ⚙️ Link detection regex
URL_RE = re.compile(r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)", re.IGNORECASE)

# 🔢 User warning tracker
user_warnings = {}

# 🚫 कितनी warning के बाद ban हो (changeable)
MAX_WARNINGS = 3  

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return
    user = message.from_user
    chat_id = update.effective_chat.id

    text = message.text or message.caption or ""
    if not URL_RE.search(text):
        return

    # 🔐 Admins को ignore करो
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ("administrator", "creator"):
            return
    except:
        pass

    # 🧹 Link delete
    try:
        await message.delete()
    except:
        pass

    # 🧮 Warning count update
    user_id = user.id
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
    warnings = user_warnings[user_id]

    # ⚠️ Warning message
    if warnings <= MAX_WARNINGS:
        remaining = MAX_WARNINGS - warnings
        warn_text = f"⚠️ @{user.username or user.first_name}, links are not allowed!\nYou have {remaining if remaining>0 else 0} warnings left before ban."
        try:
            await context.bot.send_message(chat_id=chat_id, text=warn_text)
        except:
            pass
    else:
        # 🚫 Ban user after 3 warnings
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.send_message(chat_id=chat_id, text=f"🚫 @{user.username or user.first_name} has been banned for sending too many links.")
        except Exception as e:
            print("Ban failed:", e)

if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("TELEGRAM_TOKEN not set!")
    print("Bot starting...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.run_polling()
