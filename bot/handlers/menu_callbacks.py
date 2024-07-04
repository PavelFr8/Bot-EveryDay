from aiogram import Router, F
from aiogram import types

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.back_kb import get_back_kb


menu_callback_router = Router()


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
