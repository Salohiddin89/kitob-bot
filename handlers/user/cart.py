import sqlite3
from aiogram import types
from models import get_admins
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db
from keyboards.user_menu import user_menu


def register(dp: Dispatcher):
    @dp.callback_query_handler(lambda c: c.data.startswith("addcart_"))
    async def add_to_cart(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        user_id = call.from_user.id
        db = get_db()
        db.execute("CREATE TABLE IF NOT EXISTS cart (user_id INTEGER, book_id INTEGER)")
        db.execute(
            "INSERT INTO cart (user_id, book_id) VALUES (?, ?)", (user_id, book_id)
        )
        db.commit()
        await call.message.answer("✅ Kitob savatingizga qo‘shildi.")

    @dp.message_handler(lambda msg: msg.text == "🛒 Mening savatim")
    async def view_cart(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT books.id, books.title, books.price FROM books
            JOIN cart ON books.id = cart.book_id
            WHERE cart.user_id = ?
        """,
            (msg.from_user.id,),
        )
        books = cursor.fetchall()

        if not books:
            await msg.answer(
                "🛒 Savatingiz bo‘sh. Bosh menyuga qaytdingiz.", reply_markup=user_menu
            )
            return

        kb = InlineKeyboardMarkup()
        total = 0
        text = "🛒 Savatingizdagi kitoblar:\n\n"
        for book in books:
            text += f"📘 {book['title']} — {book['price']} so‘m\n"
            total += int(book["price"])
            kb.add(
                InlineKeyboardButton(
                    book["title"], callback_data=f"cartbook_{book['id']}"
                )
            )

        text += f"\n💵 Umumiy narx: <b>{total} so‘m</b>"
        kb.add(
            InlineKeyboardButton(
                "❌ Savatdan olib tashlash", callback_data="remove_from_cart"
            ),
            InlineKeyboardButton("🧹 Savatni tozalash", callback_data="clear_cart"),
            InlineKeyboardButton("🛍 Buyurtma berish", callback_data="place_order"),
        )

        await msg.answer(text, reply_markup=kb, parse_mode="HTML")

    @dp.callback_query_handler(lambda c: c.data.startswith("cartbook_"))
    async def show_cart_book(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔙 Orqaga qaytish", callback_data="back_cart"))

        text = (
            f"📘 <b>{book['title']}</b>\n"
            f"✍️ {book['author']}\n"
            f"📄 {book['pages']} bet\n"
            f"📅 {book['year']}\n"
            f"💰 Narx: {book['price']} so‘m\n"
            f"📝 {book['description']}"
        )
        await call.message.answer_photo(
            photo=book["image"], caption=text, reply_markup=kb, parse_mode="HTML"
        )

    @dp.callback_query_handler(lambda c: c.data == "back_cart")
    async def back_to_cart(call: types.CallbackQuery):
        await view_cart(call.message)

    @dp.callback_query_handler(lambda c: c.data == "remove_from_cart")
    async def choose_remove(call: types.CallbackQuery):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT books.id, books.title FROM books
            JOIN cart ON books.id = cart.book_id
            WHERE cart.user_id = ?
        """,
            (call.from_user.id,),
        )
        books = cursor.fetchall()

        kb = InlineKeyboardMarkup()
        for book in books:
            kb.add(
                InlineKeyboardButton(
                    book["title"], callback_data=f"confirmremove_{book['id']}"
                )
            )
        await call.message.answer(
            "❌ Qaysi kitobni olib tashlamoqchisiz?", reply_markup=kb
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("confirmremove_"))
    async def confirm_remove(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
        title = cursor.fetchone()["title"]

        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Ha", callback_data=f"remove_{book_id}"),
            InlineKeyboardButton("❌ Yo‘q", callback_data="back_cart"),
        )
        await call.message.answer(
            f"Rostdan ham “{title}” kitobini olib tashlamoqchimisiz?", reply_markup=kb
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("remove_"))
    async def remove_book(call: types.CallbackQuery):
        book_id = int(call.data.split("_")[1])
        db = get_db()
        db.execute(
            "DELETE FROM cart WHERE user_id = ? AND book_id = ?",
            (call.from_user.id, book_id),
        )
        db.commit()
        await call.message.answer("✅ Kitob savatdan olib tashlandi.")
        await view_cart(call.message)

    @dp.callback_query_handler(lambda c: c.data == "clear_cart")
    async def clear_cart(call: types.CallbackQuery):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Ha, tozalash", callback_data="confirm_clear"),
            InlineKeyboardButton("❌ Yo‘q", callback_data="back_cart"),
        )
        await call.message.answer("🧹 Savatni tozalashni xohlaysizmi?", reply_markup=kb)

    @dp.callback_query_handler(lambda c: c.data == "confirm_clear")
    async def confirm_clear_cart(call: types.CallbackQuery):
        db = get_db()
        db.execute("DELETE FROM cart WHERE user_id = ?", (call.from_user.id,))
        db.commit()
        await call.message.answer("✅ Savat tozalandi.")
        await call.message.answer("🏠 Bosh menyuga qaytdingiz.", reply_markup=user_menu)

    @dp.callback_query_handler(lambda c: c.data == "place_order")
    async def place_order(call: types.CallbackQuery):
        db = get_db()
        db.row_factory = sqlite3.Row  # ✅ Bu muhim: dict-style kirish uchun
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT books.title, books.price
            FROM cart
            JOIN books ON cart.book_id = books.id
            WHERE cart.user_id = ?
        """,
            (call.from_user.id,),
        )
        items = cursor.fetchall()

        if not items:
            await call.message.answer("🛒 Savatingiz bo‘sh.")
            return

        total = 0
        text = f"📥 Yangi buyurtma!\n\n"
        text += f"👤 Ism: {call.from_user.first_name}\n"
        text += f"🔗 Username: @{call.from_user.username}\n"
        text += f"📚 Kitoblar:\n"

        for item in items:
            title = item["title"]
            price = item["price"]
            text += f"📘 {title} — {price} so‘m\n"
            total += int(price)

        text += f"\n💵 Umumiy narx: {total} so‘m"

        for admin_id in get_admins():
            await call.bot.send_message(admin_id, text)

        cursor.execute("DELETE FROM cart WHERE user_id = ?", (call.from_user.id,))
        db.commit()
        await call.message.answer("✅ Buyurtma tasdiqlandi.")
