import sqlite3

def create_db():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT,
        subject TEXT,
        time_start TEXT,
        time_end TEXT,
        room TEXT,
        weekday TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        user_id INTEGER PRIMARY KEY,
        class TEXT
    )
    ''')

    conn.commit()
    conn.close()

def add_subscriber(user_id, user_class):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO subscribers (user_id, class)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET class = excluded.class
    ''', (user_id, user_class))

    conn.commit()
    conn.close()

def remove_subscriber(user_id):
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM subscribers WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_subscribers():
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, class FROM subscribers')
    subscribers = cursor.fetchall()
    conn.close()
    return subscribers
