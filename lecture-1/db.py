import sqlite3

DB_NAME = "weather.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area TEXT,
            date TEXT,
            weather TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_weather(area, date, weather, created_at):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO weather_forecast (area, date, weather, created_at)
        VALUES (?, ?, ?, ?)
    """, (area, date, weather, created_at))
    conn.commit()
    conn.close()

def get_all_weather():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT area, date, weather FROM weather_forecast")
    rows = cur.fetchall()
    conn.close()
    return rows

