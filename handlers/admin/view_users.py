from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "👥 Foydalanuvchilar")
    async def show_users(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        text = "📋 Bot foydalanuvchilari:\n\n"
        for user in users:
            text += (
                f"👤 {user['first_name']} | @{user['username']} | ID: {user['id']}\n"
            )
        await msg.answer(text)
