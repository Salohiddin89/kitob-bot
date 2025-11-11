from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from states.AddAdmin import AddAdmin
from aiogram.dispatcher.filters import Text
from keyboards.confirm_buttons import confirm_buttons
from database import get_db


def register(dp: Dispatcher):
    @dp.message_handler(Text(equals="➕ Admin qo‘shish"))
    async def start_add_admin(msg: types.Message):
        await msg.answer("🧑‍💼 Admin ismini kiriting:")
        await AddAdmin.Name.set()

    @dp.message_handler(state=AddAdmin.Name)
    async def get_name(msg: types.Message, state: FSMContext):
        await state.update_data(name=msg.text)
        await msg.answer("🆔 Admin ID sini kiriting:")
        await AddAdmin.ID.set()

    @dp.message_handler(state=AddAdmin.ID)
    async def get_id(msg: types.Message, state: FSMContext):
        await state.update_data(id=int(msg.text))
        await msg.answer("🔗 Admin username (@siz):")
        await AddAdmin.Username.set()

    @dp.message_handler(state=AddAdmin.Username)
    async def get_username(msg: types.Message, state: FSMContext):
        await state.update_data(username=msg.text)
        data = await state.get_data()
        text = f"🧾 Admin maʼlumotlari:\n\n👤 Ismi: {data['name']}\n🆔 ID: {data['id']}\n🔗 Username: {data['username']}\n\nTasdiqlaysizmi?"
        await msg.answer(text, reply_markup=confirm_buttons("addadmin"))
        await AddAdmin.Confirm.set()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("confirm_addadmin"), state=AddAdmin.Confirm
    )
    async def confirm_add(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        db = get_db()
        db.execute(
            "INSERT OR IGNORE INTO admins (id, name, username) VALUES (?, ?, ?)",
            (data["id"], data["name"], data["username"]),
        )
        db.commit()
        await call.message.edit_text("✅ Admin muvaffaqiyatli qo‘shildi.")
        await state.finish()

    @dp.callback_query_handler(
        lambda c: c.data.startswith("cancel_addadmin"), state=AddAdmin.Confirm
    )
    async def cancel_add(call: types.CallbackQuery, state: FSMContext):
        await call.message.edit_text("❌ Admin qo‘shish bekor qilindi.")
        await state.finish()
