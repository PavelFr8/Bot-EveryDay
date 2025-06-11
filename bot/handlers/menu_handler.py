from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.db.crud import create_user
from bot.filters.chat_type import ChatTypeFilter
from bot.keyboards.menu_kb import get_menu_kb
from bot.utils.load_text import load_text

main_menu_router = Router()


# Обработчик команды /start
@main_menu_router.message(
    Command("start"),
    ChatTypeFilter(chat_type="private"),
)
async def start(message: Message) -> None:
    await message.answer(
        load_text("menu/welcome.html"),
        parse_mode="HTML",
        reply_markup=get_menu_kb(),
    )
    await create_user(message.from_user.id)


@main_menu_router.message(Command("menu"), ChatTypeFilter(chat_type="private"))
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        load_text("menu/menu.html"),
        parse_mode="HTML",
        reply_markup=get_menu_kb(),
    )


# Обработчик возвращения в главное меню
@main_menu_router.callback_query(F.data == "back")
async def menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        load_text("menu/menu.html"),
        parse_mode="HTML",
        reply_markup=get_menu_kb(),
    )
    await callback.answer()
