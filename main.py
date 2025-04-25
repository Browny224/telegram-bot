from dotenv import load_dotenv
load_dotenv()
import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request
import threading

# Telegram bot token
TOKEN = os.getenv("BOT_TOKEN")

# SQLite DB setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
conn.commit()

# Paid users set
PAID_USERS = set()

# Flask app for PayPal webhook
app = Flask(__name__)

@app.route("/paypal-webhook", methods=["POST"])
def paypal_webhook():
    data = request.json
    if data.get("event_type") == "PAYMENT.SALE.COMPLETED":
        user_id = int(data["resource"]["custom"])
        PAID_USERS.add(user_id)
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
    return "", 200

# Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in PAID_USERS:
        await update.message.reply_text("Welcome back! Here's your content.")
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open("sample.jpg", "rb"))
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open("sample.mp4", "rb"))
    else:
        await update.message.reply_text("Hi! Pay to unlock content. Use /donate.")

async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"PayPal Payment Link:\nhttps://www.paypal.com/pay?custom={user_id}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    await update.message.reply_text(f"Total Paid Users: {total}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to begin.\nUse /donate to pay.\nUse /stats to see user count.")

# Launch bot and webhook
def run_telegram_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("donate", donate))
    app_bot.add_handler(CommandHandler("stats", stats))
    app_bot.add_handler(CommandHandler("help", help_command))
    app_bot.run_polling()

def run_flask():
    app.run(port=5000)

threading.Thread(target=run_telegram_bot).start()
threading.Thread(target=run_flask).start()
