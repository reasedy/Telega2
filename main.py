import os
from quart import Quart, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler

app = Quart(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи свой класс (например, 12A), чтобы получать уведомления о следующих уроках.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove_subscriber(update.effective_user.id)
    await update.message.reply_text("Вы отписались от уведомлений.")

async def handle_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_class = update.message.text.strip()
    add_subscriber(update.effective_user.id, user_class)
    await update.message.reply_text(f"Вы подписаны на уведомления для класса {user_class}.")

@app.route('/webhook', methods=['POST'])
async def webhook():
    json_data = await request.get_json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return "OK", 200

async def initialize_application():
    """Инициализация приложения Telegram."""
    create_db()

    global application
    application = (
        ApplicationBuilder()
        .token(os.getenv("API_TOKEN"))
        .http_version("1.1")
        .connection_pool_size(100)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class))

    start_scheduler(application)

    await application.initialize()

if __name__ == "__main__":
    import asyncio

    asyncio.run(initialize_application())  # Инициализируем приложение
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8443)))
