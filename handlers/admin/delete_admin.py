from aiogram import types
from aiogram.dispatcher import Dispatcher
from database import get_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "➖ Admin o‘chirish")
    async def choose_admin(msg: types.Message):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM admins")
        admins = cursor.fetchall()
        kb = InlineKeyboardMarkup()
        for admin in admins:
            kb.add(
                InlineKeyboardButton(
                    admin["name"], callback_data=f"deladmin_{admin['id']}"
                )
            )
        await msg.answer("🗑 O‘chirmoqchi bo‘lgan adminni tanlang:", reply_markup=kb)

    @dp.callback_query_handler(lambda c: c.data.startswith("deladmin_"))
    async def confirm_delete(call: types.CallbackQuery):
        admin_id = int(call.data.split("_")[1])
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("✅ Ha", callback_data=f"confirmdel_{admin_id}"))
        kb.add(InlineKeyboardButton("❌ Yo‘q", callback_data="cancel_deladmin"))
        await call.message.edit_text(
            "Rostdan ham ushbu adminni o‘chirmoqchimisiz?", reply_markup=kb
        )

    @dp.callback_query_handler(lambda c: c.data.startswith("confirmdel_"))
    async def delete_admin(call: types.CallbackQuery):
        admin_id = int(call.data.split("_")[1])
        db = get_db()
        db.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
        db.commit()
        await call.message.edit_text("✅ Admin o‘chirildi.")

    @dp.callback_query_handler(lambda c: c.data == "cancel_deladmin")
    async def cancel_delete(call: types.CallbackQuery):
        await call.message.edit_text("❌ Admin o‘chirish bekor qilindi.")
