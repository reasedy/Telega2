import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from database import add_subscriber, remove_subscriber, create_db
from scheduler import start_scheduler

# Создание приложения FastAPI
app = FastAPI()

# Глобальная переменная для Application
application = None

# Обработчики Telegram-бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введи свой класс (например, 12A), чтобы получать уведомления о следующих уроках.")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remove_subscriber(update.effective_user.id)
    await update.message.reply_text("Вы отписались от уведомлений.")

async def handle_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_class = update.message.text.strip()
    add_subscriber(update.effective_user.id, user_class)
    await update.message.reply_text(f"Вы подписаны на уведомления для класса {user_class}.")

@app.post("/webhook")
async def webhook(request: Request):
    """Обработка входящих запросов от Telegram."""
    global application
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return {"status": "OK"}

@app.on_event("startup")
async def startup_event():
    """Инициализация Telegram-бота при старте FastAPI."""
    global application
    create_db()
    application = (
        ApplicationBuilder()
        .token(os.getenv("API_TOKEN"))
        .http_version("1.1")
        .connection_pool_size(100)
        .build()
    )

    application.request = HTTPXRequest(connect_timeout=5.0, read_timeout=5.0)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class))

    start_scheduler(application)
    await application.initialize()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
