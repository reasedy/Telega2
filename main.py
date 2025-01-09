import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler

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

def main():
    """Основной запуск бота."""
    create_db()

    # Создаём приложение Telegram
    application = (
        ApplicationBuilder()
        .token(os.getenv("7917769229:AAHrqDzs9c64KRcHpNXLJZ0V6GMpLTjsZz0"))
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

    # Установка Webhook
    application.run_webhook(
        listen="0.0.0.0",  # Слушать все подключения
        port=int(os.getenv("PORT", 10000)),  # Порт, предоставляемый Render
        webhook_url = f"https://telega2.onrender.com/webhook",
    )

if __name__ == "__main__":
    main()
