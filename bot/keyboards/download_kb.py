from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_download_kb(url) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄  Скачать", url=url)
    builder.button(text="⬅️  Назад", callback_data="back")
    builder.button(text="▶️  Скачать снова", callback_data="download")
    builder.adjust(2)
    return builder.as_markup()


def get_back_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️  Назад", callback_data="back")
    return builder.as_markup()
