from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "📞 Aloqa")
    async def contact(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM admins")
        admins = cursor.fetchall()
        text = "👨‍💼 Adminlar:\n"
        for admin in admins:
            text += f"{admin['username']}\n"
        text += "\n📱 Bog‘lanish: +998 90 910 17 70"
        await msg.answer(text)
