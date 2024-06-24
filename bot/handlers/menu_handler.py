from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.menu_kb import get_menu_kb
from bot.filters.chat_type import ChatTypeFilter
from bot.db.reqsts import save_data

main_menu_router = Router()


# Обработчик команды /start
@main_menu_router.message(
    Command("start"),
    ChatTypeFilter(chat_type="private")
)
async def start(
        message: Message,
        session: AsyncSession):
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
        reply_markup=get_menu_kb()
    )
    await save_data(session, message.from_user.id)


# Обработчик возвращения в главное меню
@main_menu_router.callback_query(F.data == 'back')
async def menu(callback: CallbackQuery, state: FSMContext):
    menu_text = (
        "👋  Привет\\! Ты снова в главном меню\\! 🎉\n\n"
        "Выбирай, что тебе по душе:\n"
        "*Напоминания* — не пропусти важное\\!\n"
        "*Видео* — смотри, когда захочешь\\!\n"
        "*Планировщик* — организуй свой день\\!\n"
        "*Прочие функции* — они тоже хороши\\!\n\n"
        "Твой бот\\-помощник всегда рядом\\! ✨"
    )
    await state.clear()
    await callback.message.edit_text(
        menu_text,
        parse_mode="MarkdownV2",
        reply_markup=get_menu_kb()
    )
    await callback.answer()
