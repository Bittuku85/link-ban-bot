import re
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ==========================
# 🔧 Configuration
# ==========================
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "7864547833:AAFc-opzjNY_hMYTZzpCF4STfNwO6zRnUFw"
AUTO_BAN = True   # True = Ban user after deleting link, False = just delete message

# Regex for link detection
URL_RE = re.compile(r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+)", re.IGNORECASE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    user = message.from_user
    text = message.text or message.caption or ""

    # Check if text contains link
    if not URL_RE.search(text):
        return

    # Ignore admins
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
        if member.status in ("administrator", "creator"):
            return
    except:
        pass

    # Try to delete the message
    try:
        await message.delete()
        await context.bot.send_message(
            chat_id=message.chat_id,
            text=f"🚫 @{user.username or user.first_name}, links are not allowed here!"
        )
    except:
        pass

    # Optionally ban user
    if AUTO_BAN:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=f"🔨 User {user.first_name} has been banned for posting links!"
            )
        except Exception as e:
            print("Ban failed:", e)


# ==========================
# 🔹 Main
# ==========================
if __name__ == "__main__":
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("❌ TELEGRAM_TOKEN not set!")

    print("🤖 Link Ban Bot Running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.run_polling()
