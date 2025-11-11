from database import get_db


def is_admin(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM admins WHERE id = ?", (user_id,))
    return cursor.fetchone() is not None
