import sqlite3
from database import create_db

def populate_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    schedule = [
        # Понедельник
        ("12A", "Physics", "08:30", "10:10", "353", "Monday"),
        ("12A", "Math", "10:15", "11:40", "223", "Monday"),
        ("12A", "ICT", "11:50", "13:40", "253", "Monday"),
        ("12A", "Mathcie", "13:50", "15:15", "223", "Monday"),

        # Вторник
        ("12A", "Math", "08:30", "10:10", "223", "Tuesday"),
        ("12A", "Kazakh Lang & Lit", "10:15", "11:40", "351", "Tuesday"),
        ("12A", "Physics", "11:50", "13:40", "133", "Tuesday"),
        ("12A", "ICT", "13:50", "15:15", "255", "Tuesday"),

        # Среда
        ("12A", "Math", "08:30", "10:10", "223", "Wednesday"),
        ("12A", "Physics", "10:15", "11:40", "256", "Wednesday"),
        ("12A", "KSM", "11:50", "13:40", "324", "Wednesday"),
        ("12A", "nvp,curator", "13:50", "15:15", "324,304", "Wednesday"),
        ("12A", "ICT", "15:35", "17:00", "255", "Wednesday"),

        # Четверг
        ("12A", "Math", "08:30", "10:10", "223", "Thursday"),
        ("12A", "musorka_CIE", "10:15", "11:40", "255", "Thursday"),
        ("12A", "Physra", "11:50", "13:40", "ozinbilesin", "Thursday"),
        ("12A", "Programming", "13:50", "15:15", "257", "Thursday"),
        ("12A", "CIE_Phys", "15:35", "17:00", "223", "Thursday"),

        # Пятница
        ("12A", "cie_ksm/kaz",  "08:30", "10:10", "351", "Friday"),
        ("12A", "Math", "10:15", "11:40", "223", "Friday"),

    ]

    cursor.execute("DELETE FROM timetable")  # Очищаем таблицу перед добавлением новых данных

    for lesson in schedule:
        cursor.execute('''
        INSERT INTO timetable (class, subject, time_start, time_end, room, weekday)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', lesson)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    populate_db()
    print("База данных успешно заполнена расписанием.")
