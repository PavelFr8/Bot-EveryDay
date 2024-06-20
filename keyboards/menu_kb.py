from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallbackFactory(CallbackData, prefix="menu"):
    action: str


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
