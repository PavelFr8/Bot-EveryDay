from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_default_plan_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝  План на день",
        callback_data="create_plan"
    )
    builder.button(
        text="⬅️  Назад", callback_data='back'
    )
    return builder.as_markup()


def get_plan_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝  Добавить",
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
    builder.button(
        text="🔄  Изменить состояние задачи",
        callback_data="change_deal"
    )
    builder.adjust(3)
    return builder.as_markup()


def get_create_plan_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅  Готово", callback_data='done_deal'
    )
    builder.button(
        text="📝  Добавить ещё",
        callback_data="more_deals"
    )

    builder.adjust(1)
    return builder.as_markup()


def get_back_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️  Назад",
        callback_data="done_deal"
    )
    return builder.as_markup()


def get_done_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅  Готово", callback_data='done_deal'
    )
    return builder.as_markup()


def get_schedule_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌  Удалить",
        callback_data='del_plan_schedule'
    )
    builder.button(
        text="📝  Добавить",
        callback_data="add_plan_schedule"
    )
    return builder.as_markup()
