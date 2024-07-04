from aiogram import Router, F
from aiogram import types

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.back_kb import get_back_kb


notification_callback_router = Router()


# Колбэк для напоминаний
@notification_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "reminder"))
async def callbacks_reminder(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '🔔 Нужно напоминание\\? *Не проблема\\!* \n\nУкажите время и событие, '
        'и я убедусь, что вы не пропустите ничего важного\\. Ваш личный органайзер всегда под рукой\\! ⏰',
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )