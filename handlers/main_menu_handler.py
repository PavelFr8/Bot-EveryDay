from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import types

from keyboards.main_menu_kb import get_main_menu_kb, MenuCallbackFactory

main_menu_router = Router()


@main_menu_router.message(Command("start"))
async def start(message: Message):
    welcome_text = (
        "Приветствую тебя, путник в мире бесконечных напоминаний и задач\\! 🌟\n\n"
        "Я *Твой Личный Ассистент Бот*, и я здесь, чтобы помочь тебе не забыть о важных вещах в этой суете жизни\\.\n\n"
        "Вот что я могу для тебя сделать:\n"
        "— Создавать *напоминания* в удобное для тебя время\n"
        "— Помогать *скачивать видео* для оффлайн просмотра\n"
        "— Составлять *план на день*, чтобы ты был в курсе своих дел\n"
        "— И многое другое, что упростит твою повседневную жизнь\n\n"
        "Давай начнем\\. Ниже находится главное меню, где можно выбрать нужную функцию\\."
    )
    await message.answer(
        welcome_text,
        parse_mode="MarkdownV2",
        reply_markup=get_main_menu_kb()
    )


@main_menu_router.callback_query(MenuCallbackFactory.filter(F.action == "download"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.answer(callback_data.action)


@main_menu_router.callback_query(MenuCallbackFactory.filter(F.action == "reminder"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.answer(callback_data.action)


@main_menu_router.callback_query(MenuCallbackFactory.filter(F.action == "plan"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.answer(callback_data.action)


@main_menu_router.callback_query(MenuCallbackFactory.filter(F.action == "other"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: MenuCallbackFactory
):
    await callback.message.answer(callback_data.action)
