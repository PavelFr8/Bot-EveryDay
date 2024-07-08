from aiogram import Router, F
from aiogram import types

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.settings_kb import get_settings_kb, get_back_kb


settings_callback_router = Router()


# Колбэк для меню настроек
@settings_callback_router.callback_query(F.data == 'back_to_settings')
@settings_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "settings"))
async def callbacks_other(
        callback: types.CallbackQuery
):
    await callback.message.edit_text(
        '⚙️ *Добро пожаловать в мои настройки\\!*\n\n Здесь вы можете изменить некоторые '
        'параметры, чтобы вам стало удобнее использовать мои функции\\.',
        parse_mode="MarkdownV2",
        reply_markup=get_settings_kb()
    )
