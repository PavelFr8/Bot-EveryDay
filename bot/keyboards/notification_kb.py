from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_notification_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🪄  Добавить", callback_data="add_notification")
    builder.button(text="❌  Удалить", callback_data="del_notification")
    builder.button(text="⬅️  Назад", callback_data="back")
    builder.adjust(2)
    return builder.as_markup()


def get_default_notification_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🪄  Добавить", callback_data="add_notification")
    builder.button(text="⬅️  Назад", callback_data="back")
    return builder.as_markup()


def get_back_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️  Назад", callback_data="back_notification")
    return builder.as_markup()


def get_done_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅  Готово", callback_data="back_notification")
    return builder.as_markup()


def get_time_kb() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text="Через 15 минут")
    builder.button(text="Через 5 минут")
    builder.button(text="Через 30 минут")
    builder.button(text="Через 1 час")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
