import sqlite3

async def db_start():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            tg_id INTEGER UNIQUE,
            phone_number TEXT
        )
    """)

    # Kinolar jadvali (Janr ustuni bilan)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_code TEXT UNIQUE,
            movie_name TEXT,
            movie_genre TEXT,
            video_id TEXT
        )
    """)
    conn.commit()
    conn.close()

# Foydalanuvchini tekshirish
async def check_user(tg_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Yangi foydalanuvchi yaratish
async def create_user(first_name, last_name, tg_id, phone_number):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (first_name, last_name, tg_id, phone_number)
        VALUES (?, ?, ?, ?)
    """, (first_name, last_name, tg_id, phone_number))
    conn.commit()
    conn.close()

# Kinolarni kod bo'yicha olish
async def get_movie(movie_code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT movie_name, video_id, movie_genre FROM movies WHERE movie_code = ?", (movie_code,))
    movie = cursor.fetchone()
    conn.close()
    return movie

# Botdagi umumiy foydalanuvchilar sonini hisoblash
async def get_users_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
