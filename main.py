import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT)")

PAID_USERS = set()  # Placeholder for paid user IDs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user.id, user.username))
    conn.commit()

    if user.id in PAID_USERS:
        await update.message.reply_text("Welcome back! Here's your exclusive content.")
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("media/sample.jpg", "rb"))
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open("media/sample.mp4", "rb"))
    else:
        await update.message.reply_text("Hi! To access exclusive content, please donate first using /donate.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Start the bot\n/donate - Support and unlock content\n/stats - View user stats")

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To unlock premium content, donate to:\nUPI: yourupi@bank\nOr send screenshot to admin.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    await update.message.reply_text(f"Total users who used the bot: {total_users}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("donate", donate))
app.add_handler(CommandHandler("stats", stats))
app.run_polling()
