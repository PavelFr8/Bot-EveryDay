from aiogram import Router, F
from aiogram import types

from keyboards.menu_kb import MenuCallbackFactory
from keyboards.back_kb import get_back_kb


menu_callback_router = Router()


# Колбэк для напоминаний
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "reminder"))
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


# Колбэк для планирования
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "plan"))
async def callbacks_plan(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '📅 *Планирование — ключ к успеху\\!* \n\nДавайте составим ваш идеальный план на день\\. '
        'Просто напишите, что вы хотите включить, и я помогу вам организовать все дела\\! 📝',
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )


# Колбэк для других запросов
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "other"))
async def callbacks_other(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '🤔 *Чем еще я могу помочь\\?* Если у вас есть вопросы или нужна помощь, '
        'просто спросите\\! Я здесь, чтобы облегчить вашу жизнь\\! ✨',
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
