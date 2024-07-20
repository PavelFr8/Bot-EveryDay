from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession
import re
import logging

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.settings_kb import get_settings_kb, get_back_kb, get_done_kb
from bot.db.reqsts import get_data_by_id

settings_callback_router = Router()


# Класс для диалога про скачивание видео
class GetTimezone(StatesGroup):
    getting_timezome = State()


# Колбэк для меню настроек
@settings_callback_router.callback_query(F.data == 'back_to_settings')
@settings_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "settings"))
async def callbacks_settings(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    data = await get_data_by_id(session, callback.from_user.id)
    await callback.message.edit_text(
        '⚙️ *Добро пожаловать в мои настройки\\!*\n\n Здесь вы можете изменить некоторые '
        'параметры, чтобы вам стало удобнее использовать мои функции\\.',
        parse_mode="MarkdownV2",
        reply_markup=get_settings_kb(data.notifications_state)
    )
    await state.clear()


# Колбэк на изменение статуса ежедневных уведомлений
@settings_callback_router.callback_query(F.data == 'change_notf_state')
async def change_notification_state(
        callback: types.CallbackQuery,
        session: AsyncSession,
        state: FSMContext
):
    data = await get_data_by_id(session, callback.from_user.id)
    if data.notifications_state:
        data.notifications_state = False
    else:
        data.notifications_state = True
    await session.commit()
    await callbacks_settings(callback, state, session)


# Колбэк для изменения часового пояса
@settings_callback_router.callback_query(F.data == 'change_timezone')
async def change_timezone(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    data = await get_data_by_id(session, callback.from_user.id)
    await state.set_state(GetTimezone.getting_timezome)
    await callback.message.edit_text(
        "*Давайте изменим часовой пояс\\!* 🕑\n\n"
        f"Текущий часовой пояс: \\+{str(data.timezone)} UTC\n\n"
        "Отправь мне *сообщение*, в котором вы укажите ваш часовой пояс\\.\n"
        "*Пример сообщения: _\\+\\3_*",
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )


# Обработчик на сообщение с данными для изменения часового пояса
@settings_callback_router.message(GetTimezone.getting_timezome)
async def get_new_timezone(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    try:
        new_timezone = int(str(message.text)[1:].strip())

        if 1 <= new_timezone <= 12:
            data = await get_data_by_id(session, message.from_user.id)
            data.timezone = new_timezone
            await session.commit()
            await state.clear()
            await message.answer(
                '*Отлично, часовой пояс успешно изменён\\!* 🕑\n'
                "*Пример сообщения: _\\+3_*",
                parse_mode="MarkdownV2",
                reply_markup=get_done_kb()
            )
        else:
            await message.answer(
                'Неверный формат часового пояса\\! Попробуйте снова\\!\n'
                "*Пример сообщения: _\\+3_*",
                parse_mode="MarkdownV2",
                reply_markup=get_back_kb()
            )

    except Exception:
        await message.answer(
            'Неверный формат часового пояса\\! Попробуйте снова\\!\n'
            "*Пример сообщения: _\\+3_*",
            parse_mode="MarkdownV2",
            reply_markup=get_back_kb()
        )
