from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db
from keyboards.user_menu import user_menu
from utils.check_admin import is_admin
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def register(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, first_name, username) VALUES (?, ?, ?)",
            (msg.from_user.id, msg.from_user.first_name, msg.from_user.username),
        )
        db.commit()

        greeting = (
            f"👋 Salom, {msg.from_user.first_name}!\nQuyidagi menyudan foydalaning:"
        )

        if is_admin(msg.from_user.id):
            # 🔧 Adminlar uchun to‘liq menyu (user + admin)
            full_menu = ReplyKeyboardMarkup(resize_keyboard=True)
            full_menu.row(
                KeyboardButton("📚 Kitoblar"), KeyboardButton("🛒 Mening savatim")
            )
            full_menu.row(KeyboardButton("ℹ️ Bot haqida"), KeyboardButton("📞 Aloqa"))
            full_menu.row(
                KeyboardButton("📚 Kitob qo‘shish"),
                KeyboardButton("❌ Kitob o‘chirish"),
            )
            full_menu.row(KeyboardButton("✏️ Kitobni tahrirlash"))
            full_menu.row(
                KeyboardButton("➕ Admin qo‘shish"),
                KeyboardButton("➖ Admin o‘chirish"),
            )
            full_menu.row(KeyboardButton("👥 Foydalanuvchilar"))
            await msg.answer(greeting, reply_markup=full_menu)
        else:
            await msg.answer(greeting, reply_markup=user_menu)
