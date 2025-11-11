from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from states.EditBook import EditBook
from database import get_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "✏️ Kitobni tahrirlash")
    async def choose_book(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title FROM books")
        books = cursor.fetchall()
        kb = InlineKeyboardMarkup()
        for book in books:
            kb.add(
                InlineKeyboardButton(
                    book["title"], callback_data=f"editbook_{book['id']}"
                )
            )
        await msg.answer("✏️ Qaysi kitobni tahrirlaysiz?", reply_markup=kb)
        await EditBook.ChooseBook.set()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("editbook_"), state=EditBook.ChooseBook
    )
    async def choose_field(call: types.CallbackQuery, state: FSMContext):
        book_id = int(call.data.split("_")[1])
        await state.update_data(book_id=book_id)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("📘 Nomi", callback_data="field_title"),
            InlineKeyboardButton("✍️ Muallif", callback_data="field_author"),
            InlineKeyboardButton("📄 Betlar", callback_data="field_pages"),
            InlineKeyboardButton("📝 Tavsif", callback_data="field_description"),
            InlineKeyboardButton("📅 Yil", callback_data="field_year"),
            InlineKeyboardButton("🖼 Rasm", callback_data="field_image"),
        )
        await call.message.edit_text("🛠 Qaysi maydonni tahrirlaysiz?", reply_markup=kb)
        await EditBook.ChooseField.set()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("field_"), state=EditBook.ChooseField
    )
    async def ask_new_value(call: types.CallbackQuery, state: FSMContext):
        field = call.data.split("_")[1]
        await state.update_data(field=field)
        field_names = {
            "title": "kitob nomini",
            "author": "muallifni",
            "pages": "betlar sonini",
            "description": "tavsifni",
            "year": "chiqqan yilini",
            "image": "rasm URL yoki fayl ID sini",
        }
        await call.message.answer(f"✏️ Yangi {field_names[field]} kiriting:")
        await EditBook.NewValue.set()

    @dp.message_handler(state=EditBook.NewValue)
    async def confirm_change(msg: types.Message, state: FSMContext):
        await state.update_data(new_value=msg.text)
        data = await state.get_data()
        field = data["field"]
        field_names = {
            "title": "Nomi",
            "author": "Muallif",
            "pages": "Betlar",
            "description": "Tavsif",
            "year": "Yil",
            "image": "Rasm",
        }
        text = f"📝 {field_names[field]} ni quyidagiga o‘zgartirmoqchimisiz?\n\n🔄 Yangi qiymat: <b>{msg.text}</b>"
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Ha", callback_data="confirm_edit"),
            InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_edit"),
        )
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")
        await EditBook.Confirm.set()

    @dp.callback_query_handler(
        lambda c: c.data == "confirm_edit", state=EditBook.Confirm
    )
    async def apply_change(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        db = get_db()
        db.execute(
            f"UPDATE books SET {data['field']} = ? WHERE id = ?",
            (data["new_value"], data["book_id"]),
        )
        db.commit()
        await call.message.edit_text("✅ O‘zgarish saqlandi.")
        await state.finish()

    @dp.callback_query_handler(
        lambda c: c.data == "cancel_edit", state=EditBook.Confirm
    )
    async def cancel_change(call: types.CallbackQuery, state: FSMContext):
        await call.message.edit_text("❌ Tahrirlash bekor qilindi.")
        await state.finish()
