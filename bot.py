from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from handlers import start
from kee_alive import keep_alive
from handlers.user import place_order
from handlers.user import cart
from handlers.admin import (
    add_admin,
    delete_admin,
    add_book,
    delete_book,
    edit_book,
    view_users,
)
from handlers.user import view_books, about_bot, contact_admins
from models import init_db, patch_books_table  # ✅ patch_books_table ni chaqiramiz

# Bot va dispatcher
bot = Bot(token=TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ma'lumotlar bazasini yaratish
init_db()

# Handlerlarni ro'yxatdan o'tkazish
start.register(dp)
add_admin.register(dp)
delete_admin.register(dp)
add_book.register(dp)
delete_book.register(dp)
edit_book.register(dp)
view_users.register(dp)
view_books.register(dp)
about_bot.register(dp)
contact_admins.register(dp)
place_order.register(dp)
cart.register(dp)

# Botni ishga tushirish
if __name__ == "__main__":
    keep_alive()
    print("📚 Kitob bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
