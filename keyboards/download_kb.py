from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_download_kb(url) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄  Скачать",
        callback_data='back',
        url=url
    )
    builder.button(
        text="⬅️  Назад", callback_data='back'
    )
    return builder.as_markup()