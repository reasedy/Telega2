import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler

# Создание приложения FastAPI
app = FastAPI()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    try:
        await update.message.reply_text(
            "Привет! Введи свой класс (например, 12A), чтобы получать уведомления о следующих уроках."
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения в start: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop."""
    try:
        remove_subscriber(update.effective_user.id)
        await update.message.reply_text("Вы отписались от уведомлений.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в stop: {e}")

async def handle_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений с классами."""
    try:
        user_class = update.message.text.strip()
        add_subscriber(update.effective_user.id, user_class)
        await update.message.reply_text(f"Вы подписаны на уведомления для класса {user_class}.")
    except Exception as e:
        print(f"Ошибка при отправке сообщения в handle_class: {e}")

@app.post("/webhook")
async def webhook(request: Request):
    """Обработка входящих запросов от Telegram."""
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    try:
        await application.process_update(update)
    except Exception as e:
        print(f"Ошибка при обработке webhook: {e}")
    return {"status": "OK"}

async def initialize_application():
    """Инициализация приложения Telegram."""
    create_db()

    global application
    application = (
        ApplicationBuilder()
        .token(os.getenv("API_TOKEN"))
        .http_version("1.1")
        .connection_pool_size(100)  # Увеличиваем размер пула соединений
        .build()
    )

    # Устанавливаем таймауты для подключения и чтения
    application.request = HTTPXRequest(connect_timeout=5.0, read_timeout=5.0)

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class))

    start_scheduler(application)

    # Инициализация приложения
    await application.initialize()

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(initialize_application())
