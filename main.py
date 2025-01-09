import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler

app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text("Привет! Введи свой класс (например, 12A), чтобы получать уведомления о следующих уроках.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop."""
    remove_subscriber(update.effective_user.id)
    await update.message.reply_text("Вы отписались от уведомлений.")

async def handle_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с классами."""
    user_class = update.message.text.strip()
    add_subscriber(update.effective_user.id, user_class)
    await update.message.reply_text(f"Вы подписаны на уведомления для класса {user_class}.")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка входящих запросов от Telegram."""
    json_data = request.get_json()
    update = Update.de_json(json_data, application.bot)
    application.process_update(update)
    return "OK", 200

def main():
    """Основной запуск бота."""
    create_db()

    # Создаём приложение Telegram
    global application
    application = (
        ApplicationBuilder()
        .token(os.getenv("API_TOKEN"))
        .http_version("1.1")
        .connection_pool_size(100)
        .build()
    )

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class))

    # Запускаем планировщик
    start_scheduler(application)

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8443)))
