from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_notification_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🪄  Добавить",
        callback_data="more_deals"
    )
    builder.button(
        text="❌  Удалить",
        callback_data="del_deal"
    )
    builder.button(
        text="⬅️  Назад",
        callback_data="back"
    )
    builder.adjust(2)
    return builder.as_markup()


def get_default_notification_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🪄  Добавить",
        callback_data="more_deals"
    )
    builder.button(
        text="⬅️  Назад",
        callback_data="back"
    )
    builder.adjust(1)
    return builder.as_markup()

