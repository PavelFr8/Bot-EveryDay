from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pytz import utc

from bot.cbdata import MenuCallbackFactory
from bot.db.crud import (
    change_deal_state,
    create_deal,
    delete_deal,
    get_user_by_id,
    get_users,
)
from bot.handlers.menu_handler import menu
from bot.keyboards.plan_kbs import (
    get_back_kb,
    get_create_plan_kb,
    get_default_plan_kb,
    get_done_kb,
    get_plan_kb,
    get_schedule_kb,
)
from bot.utils.load_text import load_text

plan_callback_router = Router()


# Класс для диалога про добавление новых задач
class GetPlan(StatesGroup):
    getting_plan = State()


# Класс для диалога про удаление задач
class GetDel(StatesGroup):
    choosing_wrong = State()


# Класс для диалога про удаление задач
class GetChanged(StatesGroup):
    choosing_changed = State()


# Колбэк для планирования
@plan_callback_router.callback_query(F.data == "done_deal")
@plan_callback_router.callback_query(F.data == "back_deal")
@plan_callback_router.callback_query(
    MenuCallbackFactory.filter(F.action == "plan"),
)
async def callbacks_plan(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_id(callback.from_user.id)
    deals_list = await user.get_beautiful_plan()
    if deals_list:
        await callback.message.edit_text(
            load_text("plan/plan.html").format(deals_list=deals_list),
            parse_mode="HTML",
            reply_markup=get_plan_kb(),
        )
    else:
        await callback.message.edit_text(
            load_text("plan/create_plan.html"),
            parse_mode="HTML",
            reply_markup=get_default_plan_kb(),
        )

    await callback.answer()
    await state.clear()


# Колбэк на создание плана на день
@plan_callback_router.callback_query(F.data == "create_plan")
async def create_plan(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        load_text("plan/new_plan.html"),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await state.set_state(GetPlan.getting_plan)
    await callback.answer()


# Колбэк на добавление новых задач
@plan_callback_router.callback_query(F.data == "more_deals")
async def add_more_deals(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        load_text("plan/add_plan.html"),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await state.set_state(GetPlan.getting_plan)
    await callback.answer()


# Обработчик для добавления новой задачи
@plan_callback_router.message(GetPlan.getting_plan)
async def add_deal(message: types.Message, state: FSMContext):
    await create_deal(message.from_user.id, message.text)
    await message.answer(
        load_text("plan/done_add_plan.html"),
        parse_mode="HTML",
        reply_markup=get_create_plan_kb(),
    )
    await state.clear()


# Колбэк на удаление задачи
@plan_callback_router.callback_query(F.data == "del_deal")
async def del_deal(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_id(callback.from_user.id)
    enum_plan = await user.get_enum_plan()
    await callback.message.edit_text(
        load_text("plan/delete_plan.html").format(enum_plan=enum_plan),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await state.set_state(GetDel.choosing_wrong)
    await callback.answer()


# Обработчик для удаления задачи
@plan_callback_router.message(GetDel.choosing_wrong)
async def get_del_deal(message: types.Message, state: FSMContext):
    await delete_deal(message.from_user.id, int(message.text))
    await message.answer(
        load_text("plan/done_delete_plan.html"),
        parse_mode="HTML",
        reply_markup=get_done_kb(),
    )
    await state.clear()


# Колбэк на изменение состояния задачи
@plan_callback_router.callback_query(F.data == "change_deal")
async def change_deal(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_id(callback.from_user.id)
    enum_plan = await user.get_enum_plan()
    await callback.message.edit_text(
        load_text("plan/change_state.html").format(enum_plan=enum_plan),
        parse_mode="HTML",
        reply_markup=get_back_kb(),
    )
    await state.set_state(GetChanged.choosing_changed)
    await callback.answer()


# Обработчик для изменения состояния задачи
@plan_callback_router.message(GetChanged.choosing_changed)
async def get_change_deal(message: types.Message, state: FSMContext):
    await change_deal_state(message.from_user.id, int(message.text))
    user = await get_user_by_id(message.from_user.id)
    deals_list = await user.get_beautiful_plan()
    await message.answer(
        load_text("plan/done_change_state.html").format(deals_list=deals_list),
        parse_mode="HTML",
        reply_markup=get_done_kb(),
    )
    await state.clear()


# Ежедневная функция оповещения о невыполненных задачах
async def scheduled_task(session_factory, bot, scheduler):
    async with session_factory() as session:
        users = await get_users(session)
        for user in users:
            if user.deals_list and user.notifications_state:
                run_time = datetime.now(utc) + timedelta(hours=user.timezone)
                run_time = run_time.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )

                if datetime.now(utc) > run_time:
                    run_time += timedelta(days=1)

                scheduler.add_job(
                    send_message,
                    "date",
                    run_date=run_time,
                    args=[bot, session, user.user_id],
                )


# Ежедневная функция оповещения о невыполненных задачах
async def send_message(bot, session, chat_id):
    user = await get_user_by_id(session, chat_id)
    deals_list = await user.get_plan_for_schedules()
    await bot.send_message(
        chat_id,
        load_text("plan/scheduled_plan.html").format(deals_list=deals_list),
        parse_mode="HTML",
        reply_markup=get_schedule_kb(),
    )


# Колбэк на добавление старых задач в новый список
@plan_callback_router.callback_query(F.data == "add_plan_schedule")
async def add_old_plan(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_id(callback.from_user.id)
    for deal in user.deals:
        if deal.is_done:
            await delete_deal(deal.id)

    await callback.answer()
    await menu(callback, state)


# Колбэк на отказ от добавления старых задач в новый список
@plan_callback_router.callback_query(F.data == "del_plan_schedule")
async def del_old_plan(callback: types.CallbackQuery, state: FSMContext):
    user = await get_user_by_id(callback.from_user.id)
    for deal in user.deals:
        await delete_deal(deal.id)

    await callback.answer()
    await menu(callback, state)
