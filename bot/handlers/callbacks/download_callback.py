from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import re
import logging

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.download_kb import get_download_kb
from bot.keyboards.back_kb import get_back_kb
from bot.api.get_video import get_video

download_callback_router = Router()


# Класс для диалога про скачивание видео
class GetUrl(StatesGroup):
    getting_url = State()


# Колбэк для скачивания видео
@download_callback_router.callback_query(StateFilter(None), MenuCallbackFactory.filter(F.action == "download"))
async def callbacks_download(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory,
        state: FSMContext
):
    await callback.message.edit_text(
        '📥 Хотите скачать видео\\? Отлично\\! \n\n'
        'Пожалуйста, отправьте мне *ссылку* на видео, '
        'и я начну процесс загрузки для вас\\. После загрузки, вы сможете его скачать\\!\n\n',
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    await callback.answer()
    await state.set_state(GetUrl.getting_url)


# Обработчик для отправки скачанного видео
@download_callback_router.message(
    GetUrl.getting_url
)
async def video(
        message: types.Message,
        state: FSMContext
):
    # Проверяем, является ли текст сообщения URL
    if re.match(r'\bhttps?://\S+\.\S+\b', message.text):
        try:
            await state.update_data(url=message.text)
            user_data = await state.get_data()
            video_url = get_video(user_data['url'])
            logging.info(f'{user_data["url"]}')
            await message.answer(text="Видео успешно скачано! ✨",
                                 reply_markup=get_download_kb(video_url))
            await state.clear()
        except Exception as e:
            await message.answer(
                text="Ой, кажется, я не могу скачать это видео...",
                reply_markup=get_back_kb()
            )
            logging.error(f'Bot fail downloading video: {e}')
    else:
        await message.answer(
            text="Кажется, вы прислали не ссылку.",
            reply_markup=get_back_kb()
        )


@download_callback_router.callback_query(StateFilter(None), F.data == "download_more")
async def callbacks_more_video(
        callback: types.CallbackQuery,
        state: FSMContext
):
    await callback.message.edit_text(
        '📥 Видео много не бывает\\! \n\n'
        'Пожалуйста, отправьте мне *ссылку* на видео, '
        'и я начну процесс загрузки для вас\\. После загрузки, вы сможете его скачать\\!\n\n',
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    await state.set_state(GetUrl.getting_url)
    await callback.answer()
