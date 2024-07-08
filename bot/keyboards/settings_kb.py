from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_settings_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🕑  Изменить часовой пояс",
        callback_data="change_timezone"
    )
    builder.button(
        text="Уведомления о плане на день: ✅",
        callback_data="change_notf_state"
    )
    builder.button(
        text="⬅️  Назад", callback_data='back'
    )
    builder.adjust(1)
    return builder.as_markup()


def get_back_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️  Назад", callback_data='back_to_settings'
    )
    return builder.as_markup()
