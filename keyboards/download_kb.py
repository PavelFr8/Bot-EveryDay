from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_download_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️  Назад", callback_data='back'
    )
    return builder.as_markup()