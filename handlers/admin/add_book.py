from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from states.AddBook import AddBook
from keyboards.confirm_buttons import confirm_buttons
from database import get_db
from utils.check_admin import is_admin


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "📚 Kitob qo‘shish")
    async def start_add_book(msg: types.Message):
        if not is_admin(msg.from_user.id):
            await msg.answer("❌ Siz admin emassiz.")
            return
        await msg.answer("📘 Kitob nomini kiriting:")
        await AddBook.Title.set()

    @dp.message_handler(state=AddBook.Title)
    async def get_title(msg: types.Message, state: FSMContext):
        await state.update_data(title=msg.text)
        await msg.answer("✍️ Muallif ismini kiriting:")
        await AddBook.Author.set()

    @dp.message_handler(state=AddBook.Author)
    async def get_author(msg: types.Message, state: FSMContext):
        await state.update_data(author=msg.text)
        await msg.answer("📄 Betlar sonini kiriting:")
        await AddBook.Pages.set()

    @dp.message_handler(state=AddBook.Pages)
    async def get_pages(msg: types.Message, state: FSMContext):
        await state.update_data(pages=int(msg.text))
        await msg.answer("📝 Kitob haqida qisqacha maʼlumot:")
        await AddBook.Description.set()

    @dp.message_handler(state=AddBook.Description)
    async def get_description(msg: types.Message, state: FSMContext):
        await state.update_data(description=msg.text)
        await msg.answer("📅 Chiqqan yilini kiriting:")
        await AddBook.Year.set()

    @dp.message_handler(state=AddBook.Year)
    async def get_year(msg: types.Message, state: FSMContext):
        await state.update_data(year=int(msg.text))
        await msg.answer(
            "🖼 Kitob rasmlarini yuboring (maks. 3 ta). Har birini alohida yuboring. Tugatgach /next deb yozing:"
        )
        await AddBook.Images.set()

    @dp.message_handler(content_types=["text", "photo"], state=AddBook.Images)
    async def get_images(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        images = data.get("images", [])

        if msg.photo:
            file_id = msg.photo[-1].file_id
        else:
            file_id = msg.text

        images.append(file_id)
        await state.update_data(images=images)

        if len(images) < 3:
            await msg.answer(
                f"🖼 {len(images)}-rasm qabul qilindi. Yana rasm yuboring yoki /next buyrug‘ini bosing."
            )
        else:
            await msg.answer("✅ 3 ta rasm qabul qilindi.")
            await AddBook.price.set()
            await msg.answer("💰 Kitob narxini kiriting (so‘mda):")

    @dp.message_handler(commands="next", state=AddBook.Images)
    async def finish_images(msg: types.Message, state: FSMContext):
        data = await state.get_data()
        images = data.get("images", [])
        if not images:
            await msg.answer(
                "❗️Hech qanday rasm topilmadi. Iltimos, kamida bitta rasm yuboring."
            )
            return
        await AddBook.price.set()
        await msg.answer("💰 Kitob narxini kiriting (so‘mda):")

    @dp.message_handler(state=AddBook.price)
    async def confirm_book_preview(msg: types.Message, state: FSMContext):
        price_text = msg.text.strip()
        await state.update_data(price=price_text)
        data = await state.get_data()
        text = (
            f"📘 <b>{data['title']}</b>\n"
            f"✍️ Muallif: {data['author']}\n"
            f"📄 Betlar: {data['pages']}\n"
            f"📅 Yil: {data['year']}\n"
            f"💰 Narx: {data['price']} so‘m\n"
            f"📝 Tavsif: {data['description']}\n\n"
            "✅ Tasdiqlaysizmi?"
        )
        await msg.answer(
            text, reply_markup=confirm_buttons("addbook"), parse_mode="HTML"
        )
        await AddBook.Confirm.set()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("confirm_addbook"), state=AddBook.Confirm
    )
    async def confirm_book(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        db = get_db()
        cursor = db.cursor()

        # Kitobni qo‘shish
        cursor.execute(
            """
            INSERT INTO books (title, author, pages, description, year, price)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data["title"],
                data["author"],
                data["pages"],
                data["description"],
                data["year"],
                data["price"],
            ),
        )
        book_id = cursor.lastrowid

        # Rasmlarni alohida jadvalga yozish
        for img in data.get("images", []):
            cursor.execute(
                "INSERT INTO book_images (book_id, image) VALUES (?, ?)",
                (book_id, img),
            )

        db.commit()
        await call.message.edit_text("✅ Kitob muvaffaqiyatli qo‘shildi.")
        await state.finish()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("cancel_addbook"), state=AddBook.Confirm
    )
    async def cancel_book(call: types.CallbackQuery, state: FSMContext):
        await call.message.edit_text("❌ Kitob qo‘shish bekor qilindi.")
        await state.finish()
