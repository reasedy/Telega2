from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from telegram.ext import Application
from database import get_subscribers
import pytz
import sqlite3
import asyncio

KZ_TIMEZONE = pytz.timezone("Asia/Oral")

def get_current_lesson(user_class, current_time):
    """
    Получить текущий урок, который заканчивается в данный момент.
    """
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    today = current_time.strftime("%A")
    current_time_str = current_time.strftime("%H:%M")

    cursor.execute('''
        SELECT subject, room, time_start, time_end
        FROM timetable
        WHERE class = ? AND weekday = ? AND time_end = ?
        ORDER BY time_start ASC LIMIT 1
    ''', (user_class, today, current_time_str))

    result = cursor.fetchone()
    conn.close()
    return result

def get_next_lesson(user_class, current_time):
    """
    Получить следующий урок после текущего времени.
    """
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    today = current_time.strftime("%A")
    current_time_str = current_time.strftime("%H:%M")

    cursor.execute('''
        SELECT subject, room, time_start, time_end
        FROM timetable
        WHERE class = ? AND weekday = ? AND time_start > ?
        ORDER BY time_start ASC LIMIT 1
    ''', (user_class, today, current_time_str))

    result = cursor.fetchone()
    conn.close()
    return result

async def send_notifications(application: Application):
    """
    Отправить уведомления о следующем уроке после завершения текущего.
    """
    subscribers = get_subscribers()
    now = datetime.now(KZ_TIMEZONE)

    for user_id, user_class in subscribers:
        try:
            # Проверяем текущий урок, который заканчивается сейчас
            current_lesson = get_current_lesson(user_class, now)
            if current_lesson:
                # Извлекаем следующий урок
                next_lesson = get_next_lesson(user_class, now)
                if next_lesson:
                    next_subject, next_room, next_start, _ = next_lesson
                    message = f"Следующий урок: {next_subject}, кабинет: {next_room} (в {next_start})"
                else:
                    message = "Уроки на сегодня закончились."

                # Отправляем сообщение пользователю
                await application.bot.send_message(chat_id=user_id, text=message)

        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

def start_scheduler(application: Application):
    """
    Запуск планировщика для проверки каждые 1 минуту.
    """
    scheduler = BackgroundScheduler()

    # Обёртка для выполнения асинхронной задачи
    def job_wrapper():
        asyncio.run(send_notifications(application))

    # Планировщик с интервалом 1 минута
    scheduler.add_job(job_wrapper, "interval", minutes=1)
    scheduler.start()
