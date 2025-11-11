from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from states.PlaceOrder import PlaceOrder
from database import get_db
from keyboards.user_menu import user_menu


def register(dp: Dispatcher):
    @dp.callback_query_handler(lambda c: c.data == "place_order")
    async def start_order(call: types.CallbackQuery, state: FSMContext):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT books.title FROM books JOIN cart ON books.id = cart.book_id WHERE cart.user_id = ?",
            (call.from_user.id,),
        )
        books = cursor.fetchall()

        if not books:
            await call.message.answer(
                "🛒 Savatingiz bo‘sh. Bosh menyuga qaytdingiz.", reply_markup=user_menu
            )
            return

        await call.message.answer("👤 Ismingizni kiriting:")
        await PlaceOrder.Name.set()

    @dp.message_handler(state=PlaceOrder.Name)
    async def get_name(msg: types.Message, state: FSMContext):
        await state.update_data(name=msg.text)
        await msg.answer("🔗 Telegram username'ingizni kiriting (@siz):")
        await PlaceOrder.Username.set()

    @dp.message_handler(state=PlaceOrder.Username)
    async def get_username(msg: types.Message, state: FSMContext):
        await state.update_data(username=msg.text)
        await msg.answer("📞 Telefon raqamingizni kiriting:")
        await PlaceOrder.Phone.set()

    @dp.message_handler(state=PlaceOrder.Phone)
    async def get_phone(msg: types.Message, state: FSMContext):
        await state.update_data(phone=msg.text)

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT books.title FROM books JOIN cart ON books.id = cart.book_id WHERE cart.user_id = ?",
            (msg.from_user.id,),
        )
        books = cursor.fetchall()
        book_list = "\n".join([f"📘 {b['title']}" for b in books])

        data = await state.get_data()
        text = (
            f"🧾 Buyurtma maʼlumotlari:\n\n"
            f"👤 Ism: {data['name']}\n"
            f"🔗 Username: {data['username']}\n"
            f"📞 Telefon: {data['phone']}\n"
            f"📚 Kitoblar:\n{book_list}\n\n"
            "✅ Tasdiqlaysizmi?"
        )

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("✅ Ha", callback_data="confirm_order"),
            types.InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_order"),
        )
        await msg.answer(text, reply_markup=kb)
        await PlaceOrder.Confirm.set()

    @dp.callback_query_handler(
        lambda c: c.data == "confirm_order", state=PlaceOrder.Confirm
    )
    async def confirm_order(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT books.title FROM books JOIN cart ON books.id = cart.book_id WHERE cart.user_id = ?",
            (call.from_user.id,),
        )
        books = cursor.fetchall()
        book_list = "\n".join([f"📘 {b['title']}" for b in books])

        # Adminlarga yuborish
        cursor.execute("SELECT id FROM admins")
        admins = cursor.fetchall()
        for admin in admins:
            await call.bot.send_message(
                admin["id"],
                f"📥 Yangi buyurtma!\n\n"
                f"👤 Ism: {data['name']}\n"
                f"🔗 Username: {data['username']}\n"
                f"📞 Telefon: {data['phone']}\n"
                f"📚 Kitoblar:\n{book_list}",
            )

        # Savatni tozalash
        db.execute("DELETE FROM cart WHERE user_id = ?", (call.from_user.id,))
        db.commit()

        await call.message.answer(
            "✅ Buyurtmangiz qabul qilindi. Adminlar tez orada siz bilan bog‘lanishadi.",
            reply_markup=user_menu,
        )
        await state.finish()

    @dp.callback_query_handler(
        lambda c: c.data == "cancel_order", state=PlaceOrder.Confirm
    )
    async def cancel_order(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer("❌ Buyurtma bekor qilindi.", reply_markup=user_menu)
        await state.finish()
