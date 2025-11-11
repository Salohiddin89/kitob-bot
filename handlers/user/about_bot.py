from aiogram import types
from aiogram.dispatcher import Dispatcher


def register(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "ℹ️ Bot haqida")
    async def about(msg: types.Message):
        text = (
            "📚 Bu bot orqali siz turli kitoblarni ko‘rishingiz va tanlashingiz mumkin.\n"
            "🛒 Har bir kitob haqida to‘liq ma’lumotlar mavjud.\n"
            "👨‍💼 Adminlar tomonidan doimiy yangilanadi.\n"
            "✅ Foydalanish juda oson — menyudan kerakli bo‘limni tanlang!"
        )
        await msg.answer(text)
