from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "❌ Kitob o‘chirish")
    async def choose_book(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title FROM books")
        books = cursor.fetchall()
        kb = types.InlineKeyboardMarkup()
        for book in books:
            kb.add(
                types.InlineKeyboardButton(
                    book["title"], callback_data=f"delbook_{book['id']}"
                )
            )
        await msg.answer("🗑 O‘chirmoqchi bo‘lgan kitobni tanlang:", reply_markup=kb)

    @dp.callback_query_handler(lambda c: c.data.startswith("delbook_"))
    async def confirm_delete(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton(
                "✅ Ha", callback_data=f"confirmdelbook_{book_id}"
            )
        )
        kb.add(types.InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_delbook"))
        await call.message.edit_text(
            "Rostdan ham ushbu kitobni o‘chirmoqchimisiz?", reply_markup=kb
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("confirmdelbook_"))
    async def delete_book(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        db = get_db()
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        db.commit()
        await call.message.edit_text("✅ Kitob o‘chirildi.")

    @dp.callback_query_handler(lambda c: c.data == "cancel_delbook")
    async def cancel_delete(call: types.CallbackQuery):
        await call.message.edit_text("❌ Kitob o‘chirish bekor qilindi.")
