from database import get_db
from config import ADMIN_IDS


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        pages INTEGER,
        description TEXT,
        year INTEGER,
        image TEXT,
        price INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER,
        book_id INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT
    )""")

    for admin_id in ADMIN_IDS:
        cursor.execute(
            "INSERT OR IGNORE INTO admins (id, name, username) VALUES (?, ?, ?)",
            (admin_id, "Asosiy admin", "admin"),
        )

    db.commit()


def patch_books_table():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN price INTEGER")
        db.commit()
        print("✅ 'price' ustuni qo‘shildi.")
    except Exception as e:
        print("⚠️ price ustuni allaqachon mavjud yoki xatolik:", e)


def get_admins():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM admins")
    rows = cursor.fetchall()
    return [row["id"] for row in rows]
