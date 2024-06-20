from aiogram import Router, F
from aiogram import types

from keyboards.menu_kb import MenuCallbackFactory
from keyboards.download_kb import get_download_kb


menu_callback_router = Router()


# Колбэк для скачивания видео
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "download"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '📥 Хотите скачать видео\\? Отлично\\! \n\n'
        'Пожалуйста, отправьте мне *ссылку* на видео, '
        'и я начну процесс загрузки для вас\\. После загрузки я пришлю вам *файл*, чтобы вы могли его скачать\\!\n\n'
        '❗️Доступны только видео *менее* 50 МБ',
        parse_mode="MarkdownV2",
        reply_markup=get_download_kb()
    )


# Колбэк для напоминаний
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "reminder"))
async def callbacks_reminder(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '🔔 *Нужно напоминание\\?* Не проблема\\! Укажите время и событие, '
        'и я убедусь, что вы не пропустите ничего важного\\. Ваш личный органайзер всегда под рукой\\! ⏰',
        parse_mode="MarkdownV2",
        reply_markup=get_download_kb()
    )


# Колбэк для планирования
@menu_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "plan"))
async def callbacks_plan(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.edit_text(
        '📅 *Планирование — ключ к успеху\\!* Давайте составим ваш идеальный план на день\\. '
        'Просто скажите, что вы хотите включить, и я помогу вам организовать все дела\\! 📝',
        parse_mode="MarkdownV2",
        reply_markup=get_download_kb()
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
        reply_markup=get_download_kb()
    )
