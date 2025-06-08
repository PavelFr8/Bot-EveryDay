from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.crud import save_data
from bot.filters.chat_type import ChatTypeFilter
from bot.keyboards.menu_kb import get_menu_kb
from bot.utils.load_text import load_text

main_menu_router = Router()


# Обработчик команды /start
@main_menu_router.message(
    Command("start"),
    ChatTypeFilter(chat_type="private"),
)
async def start(message: Message, session: AsyncSession) -> None:
    wellcome_text = load_text("wellcome.html")
    await message.answer(
        wellcome_text,
        parse_mode="HTML",
        reply_markup=get_menu_kb(),
    )
    await save_data(session, message.from_user.id)


@main_menu_router.message(Command("menu"), ChatTypeFilter(chat_type="private"))
async def main_menu(message: Message, state: FSMContext) -> None:
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
    await message.answer(
        menu_text,
        parse_mode="MarkdownV2",
        reply_markup=get_menu_kb(),
    )


# Обработчик возвращения в главное меню
@main_menu_router.callback_query(F.data == "back")
async def menu(callback: CallbackQuery, state: FSMContext) -> None:
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
        reply_markup=get_menu_kb(),
    )
    await callback.answer()
