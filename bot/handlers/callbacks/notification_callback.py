from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.cbdata import MenuCallbackFactory
from bot.config_reader import config
from bot.keyboards.notification_kb import (
    get_back_kb,
    get_default_notification_kb,
    get_done_kb,
    get_time_kb,
)
from bot.utils.load_text import load_text

notification_callback_router = Router()


# Класс для диалога про добавление нового напоминания
class GetNotification(StatesGroup):
    getting_name = State()
    getting_time = State()


# функция для отправки напоминания через scheduler
async def new_notification(notification: str, chat_id: int):
    # отправляем напоминание
    bot = Bot(token=config.bot_token.get_secret_value())
    await bot.send_message(
        chat_id,
        load_text("notifications/new.html").format(notification=notification),
        parse_mode="HTML",
    )
    await bot.session.close()


# Колбэк для напоминаний
@notification_callback_router.callback_query(F.data == "back_notification")
@notification_callback_router.callback_query(
    MenuCallbackFactory.filter(F.action == "reminder"),
)
async def callback_reminder(callback: types.CallbackQuery, state: FSMContext):
    text = load_text("notifications/create.html")
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_default_notification_kb(),
    )

    await state.clear()


# Колбэк на создание имени для уведомления
@notification_callback_router.callback_query(F.data == "add_notification")
async def add_notification(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        load_text("notifications/add.html"),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    fsm_data = await state.get_data()
    fsm_data["message"] = callback.message
    await state.set_data(fsm_data)
    await state.set_state(GetNotification.getting_name)
    await callback.answer()


# Обработчик для добавления нового уведомления
@notification_callback_router.message(GetNotification.getting_name)
async def add_deal(message: types.Message, state: FSMContext):
    fsm_data = await state.get_data()
    fsm_data["notification"] = message.text
    old_message = fsm_data["message"]
    await state.set_data(fsm_data)
    await old_message.edit_text(
        load_text("notifications/next_step.html"),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await message.answer(
        text=load_text("notifications/time.html"),
        parse_mode="HTML",
        reply_markup=get_time_kb(),
    )
    await state.set_state(GetNotification.getting_time)


# Обработчик для добавления времени для нового уведомления
@notification_callback_router.message(GetNotification.getting_time)
async def add_time(
    message: types.Message,
    state: FSMContext,
    scheduler: AsyncIOScheduler,
):
    fsm_data = await state.get_data()

    match message.text.lower().strip():
        case "через 5 минут":
            minutes = 5
        case "через 1 час":
            minutes = 60
        case "через 15 минут":
            minutes = 15
        case "через 30 минут":
            minutes = 30

    await message.answer(
        text=load_text("notifications/success.html"),
        parse_mode="HTML",
        reply_markup=get_done_kb(),
    )

    run_time = datetime.now() + timedelta(minutes=int(minutes))
    text = fsm_data["notification"]
    chat_id = message.from_user.id

    scheduler.add_job(
        new_notification,
        "date",
        run_date=run_time,
        args=[text, chat_id],
    )
    await state.set_state(GetNotification.getting_time)
