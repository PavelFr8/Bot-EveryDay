import re

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot import logger
from bot.api.get_video import get_video
from bot.cbdata import MenuCallbackFactory
from bot.keyboards.download_kb import get_back_kb, get_download_kb
from bot.utils.load_text import load_text

download_callback_router = Router()


# Класс для диалога про скачивание видео
class GetUrl(StatesGroup):
    getting_url = State()


# Колбэк для скачивания видео
@download_callback_router.callback_query(
    StateFilter(None),
    MenuCallbackFactory.filter(F.action == "download"),
)
@download_callback_router.callback_query(
    StateFilter(None),
    F.data == "download",
)
async def callbacks_download(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        load_text("downloads/download.html"),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await callback.answer()
    await state.set_state(GetUrl.getting_url)


# Обработчик для отправки скачанного видео
@download_callback_router.message(GetUrl.getting_url)
async def video(message: types.Message, state: FSMContext):
    if re.match(r"\bhttps?://\S+\.\S+\b", message.text):
        try:
            await state.update_data(url=message.text)
            user_data = await state.get_data()
            video_url = await get_video(user_data["url"])
            await message.answer(
                text=load_text("downloads/success.html"),
                reply_markup=get_download_kb(video_url["url"]),
            )
            await state.clear()
        except Exception as e:
            await message.answer(
                text=load_text("downloads/wrong_url.html"),
                reply_markup=get_back_kb(),
            )
            await logger.error(f"Bot fail downloading video: {e}")
    else:
        await message.answer(
            text=load_text("downloads/error.html"),
            reply_markup=get_back_kb(),
        )
