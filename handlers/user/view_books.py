from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "📚 Kitoblar")
    async def list_books(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title FROM books")
        books = cursor.fetchall()
        kb = InlineKeyboardMarkup()
        for book in books:
            kb.add(
                InlineKeyboardButton(book["title"], callback_data=f"book_{book['id']}")
            )
        await msg.answer("📖 Kitoblar ro‘yxati:", reply_markup=kb)

    @dp.callback_query_handler(lambda c: c.data.startswith("book_"))
    async def show_book(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        # Savatga qo‘shish tugmalari
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton(
                "➕ Savatga qo‘shish", callback_data=f"addcart_{book_id}"
            ),
            InlineKeyboardButton("🔙 Orqaga qaytish", callback_data="back_books"),
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu"),
        )

        text = (
            f"📘Kitob Nomi: <b>{book['title']}</b>\n"
            f"✍️Kitob Yozuvchisi: {book['author']}\n"
            f"📄Kitob {book['pages']} betdan iborat\n"
            f"📅Kitob {book['year']}yilda chiqan\n"
            f"💰Kitob narxi: <b>{book['price']} so‘m</b>\n"
            f"📝Kitob xaqida qisqacha malumot: {book['description']}"
        )

        await call.message.answer_photo(
            photo=book["image"], caption=text, reply_markup=kb, parse_mode="HTML"
        )

    @dp.callback_query_handler(lambda c: c.data == "back_books")
    async def back_to_books(call: types.CallbackQuery):
        await list_books(call.message)

    @dp.callback_query_handler(lambda c: c.data == "main_menu")
    async def back_to_main(call: types.CallbackQuery):
        from keyboards.user_menu import user_menu

        await call.message.answer("🏠 Bosh menyuga qaytdingiz.", reply_markup=user_menu)
