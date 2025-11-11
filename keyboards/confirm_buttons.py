from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_buttons(action):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Tasdiqlayman", callback_data=f"confirm_{action}"))
    kb.add(InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_{action}"))
    return kb
