from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


user_menu = ReplyKeyboardMarkup(resize_keyboard=True)
user_menu.add(KeyboardButton("📚 Kitoblar"), KeyboardButton("🛒 Mening savatim"))
user_menu.add(KeyboardButton("ℹ️ Bot haqida"), KeyboardButton("📞 Aloqa"))
