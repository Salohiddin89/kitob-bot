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
        await msg.answer("🖼 Kitob rasmi (URL yoki fayl sifatida):")
        await AddBook.Image.set()

    @dp.message_handler(content_types=["text", "photo"], state=AddBook.Image)
    async def get_image(msg: types.Message, state: FSMContext):
        if msg.photo:
            file_id = msg.photo[-1].file_id
        else:
            file_id = msg.text
        await state.update_data(image=file_id)
        await msg.answer("💰 Kitob narxini kiriting (so‘mda):")
        await AddBook.price.set()

    @dp.message_handler(state=AddBook.price)
    async def confirm_book_preview(msg: types.Message, state: FSMContext):
        await state.update_data(price=int(msg.text))
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
        db.execute(
            """
            INSERT INTO books (title, author, pages, description, year, image, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                data["title"],
                data["author"],
                data["pages"],
                data["description"],
                data["year"],
                data["image"],
                data["price"],
            ),
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
