from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add(KeyboardButton("➕ Admin qo‘shish"))
admin_menu.add(KeyboardButton("➖ Admin o‘chirish"))
admin_menu.add(KeyboardButton("📚 Kitob qo‘shish"))
admin_menu.add(KeyboardButton("❌ Kitob o‘chirish"))
admin_menu.add(KeyboardButton("✏️ Kitobni tahrirlash"))
admin_menu.add(KeyboardButton("👥 Foydalanuvchilar"))
