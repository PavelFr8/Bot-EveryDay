from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import MenuCallbackFactory


def get_menu_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎥  Скачать видео", callback_data=MenuCallbackFactory(action="download")
    )
    builder.button(
        text="🔔  Напоминание", callback_data=MenuCallbackFactory(action="reminder")
    )
    builder.button(
        text="📅  План на день", callback_data=MenuCallbackFactory(action="plan")
    )
    builder.button(
        text="✨  Другие функции", callback_data=MenuCallbackFactory(action="other")
    )
    builder.adjust(2)
    return builder.as_markup()
