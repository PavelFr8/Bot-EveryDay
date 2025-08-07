from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.cbdata import MenuCallbackFactory
from bot.db.crud import change_notify_state, change_timezone, get_user_by_id
from bot.keyboards.settings_kb import get_back_kb, get_done_kb, get_settings_kb
from bot.utils.load_text import load_text

settings_callback_router = Router()


# Класс для диалога про скачивание видео
class GetTimezone(StatesGroup):
    getting_timezome = State()


# Колбэк для меню настроек
@settings_callback_router.callback_query(F.data == "back_to_settings")
@settings_callback_router.callback_query(
    MenuCallbackFactory.filter(F.action == "settings"),
)
async def callbacks_settings(callback: types.CallbackQuery, state: FSMContext):
    data = await get_user_by_id(callback.from_user.id)
    await callback.message.edit_text(
        load_text("settings/settings.html"),
        parse_mode="HTML",
        reply_markup=get_settings_kb(data.notify_state),
    )
    await state.clear()


# Колбэк на изменение статуса ежедневных уведомлений
@settings_callback_router.callback_query(F.data == "change_notf_state")
async def change_notification_state(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    await change_notify_state(callback.from_user.id)

    await callbacks_settings(callback, state)


# Колбэк для изменения часового пояса
@settings_callback_router.callback_query(F.data == "change_timezone")
async def change_tz(callback: types.CallbackQuery, state: FSMContext):
    data = await get_user_by_id(callback.from_user.id)
    await state.set_state(GetTimezone.getting_timezome)

    await callback.message.edit_text(
        load_text("settings/timezone.html").format(timezone=data.timezone),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )


# Обработчик на сообщение с данными для изменения часового пояса
@settings_callback_router.message(GetTimezone.getting_timezome)
async def get_new_timezone(message: types.Message, state: FSMContext):
    try:
        new_timezone = int(message.text.strip()[1:])

        if 1 <= new_timezone <= 12:
            await change_timezone(message.from_user.id, new_timezone)
            await state.clear()
            await message.answer(
                load_text("settings/timezone_success.html"),
                parse_mode="HTML",
                reply_markup=get_done_kb(),
            )
        else:
            await message.answer(
                load_text("settings/timezone_error.html"),
                parse_mode="HTML",
                reply_markup=get_back_kb(),
            )

    except Exception:
        await message.answer(
            load_text("settings/timezone_error.html"),
            parse_mode="HTML",
            reply_markup=get_back_kb(),
        )
