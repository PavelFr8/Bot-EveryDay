from datetime import datetime, timedelta
from pytz import utc


from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from cbdata import MenuCallbackFactory
from keyboards.plan_kbs import (get_plan_kb, get_default_plan_kb, get_create_plan_kb, get_back_kb, get_done_kb,
                                    get_schedule_kb)
from db.reqsts import get_data_by_id, save_data, get_users
from handlers.menu_handler import menu

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


# Функция для создания красивого списка задач
def create_beautiful_plan(data: str):
    text = data.split("),(")
    back_text = ''
    for elem in text:
        if bool(int(elem[0])):
            back_text += "✅   " + f"<s>{elem[1:]}</s>" + '\n'
        else:
            back_text += "<b>•</b>  " + elem[1:] + '\n'
    return back_text


# Функция для создания красивого списка НЕ ВЫПОЛНЕННЫХ задач
def create_plan_for_schedules(data: str):
    text = data.split("),(")
    back_text = ''
    for elem in text:
        if bool(int(elem[0])):
            back_text += ''
        else:
            back_text += "<b>•</b>  " + elem[1:] + '\n'
    return back_text


# Функция для создания красивого пронумерованного списка задач
def create_enum_plan(data: str):
    text = data.split("),(")
    back_text = ''
    i = 1
    for elem in text:
        if bool(int(elem[0])):
            back_text += "✅   " + elem[1:] + f" - <b>{i}</b>" + '\n'
        else:
            back_text += "<b>•</b>  " + elem[1:] + f" - <b>{i}</b>" + '\n'
        i += 1
    return back_text


# Колбэк для планирования
@plan_callback_router.callback_query(F.data == 'done_deal')
@plan_callback_router.callback_query(F.data == 'back_deal')
@plan_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "plan"))
async def callbacks_plan(
        callback: types.CallbackQuery,
        session: AsyncSession,
        state: FSMContext):
    data = await get_data_by_id(session, callback.from_user.id)
    if data.deals_list:
        deals_list = create_beautiful_plan(data.deals_list)
        await callback.message.edit_text(
            '📅  <b>Планирование — ключ к успеху!</b>\n\n'
            f'🖋 А вот и составленный специально для вас <b>план на сегодня</b>: \n{deals_list}',
            parse_mode="HTML",
            reply_markup=get_plan_kb()
        )
    else:
        await callback.message.edit_text(
            '📅 *Планирование — ключ к успеху\\!* \n\nДавайте составим ваш идеальный план на день\\. '
            'Просто выберите нужную функцию, и я помогу вам организовать все дела\\!',
            parse_mode="MarkdownV2",
            reply_markup=get_default_plan_kb()
        )
    await callback.answer()
    await state.clear()


# Колбэк на создание плана на день
@plan_callback_router.callback_query(F.data == 'create_plan')
async def create_plan(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.edit_text(
        "*Давай создадим план на сегодня\\!* 📅\n\n"
        "Отправь мне *сообщение*, а я добавлю его в план на день\\.\n\n"
        "*Пример сообщения: _Сходить в магазин_*",
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    await state.set_state(GetPlan.getting_plan)
    await callback.answer()


# Колбэк на добавление новых задач
@plan_callback_router.callback_query(F.data == 'more_deals')
async def add_more_deals(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.edit_text(
        "*Задач мало не бывает\\!* ⚡️\n\n"
        "Отправь мне *сообщение*, а я добавлю его в план на день\\.\n\n"
        "*Пример сообщения: _Сходить в магазин_*",
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    await state.set_state(GetPlan.getting_plan)
    await callback.answer()


# Обработчик для добавления новой задачи
@plan_callback_router.message(GetPlan.getting_plan)
async def add_deal(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession):
    fsm_data = await state.get_data()
    fsm_data["deals"] = message.text
    fsm_data["notifications"] = ''
    await save_data(session, message.from_user.id, fsm_data)
    await message.answer(
        "*Отлично\\!* \nЯ добавил задачу в план на день\\! ⚡️",
        parse_mode="MarkdownV2",
        reply_markup=get_create_plan_kb()
    )
    await state.clear()


# Колбэк на удаление задачи
@plan_callback_router.callback_query(F.data == 'del_deal')
async def del_deal(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession):
    data = await get_data_by_id(session, callback.from_user.id)
    enum_deals_list = create_enum_plan(data.deals_list)
    await callback.message.edit_text(
        "<b>Задач бывает и много!</b> ⚡️\n\n"
        "Отправь мне <b>номер</b> задачи, которую нужно удалить.\n\n"
        f"{enum_deals_list}",
        parse_mode="HTML",
        reply_markup=get_back_kb()
    )
    await state.set_state(GetDel.choosing_wrong)
    await callback.answer()


# Обработчик для удаления задачи
@plan_callback_router.message(GetDel.choosing_wrong)
async def get_del_deal(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession):
    data = await get_data_by_id(session, message.from_user.id)
    data.deals_list = data.deals_list.split("),(")
    del data.deals_list[int(message.text) - 1]
    data.deals_list = "),(".join(data.deals_list)
    await session.commit()
    await message.answer(
        "*Отлично\\!* \nЯ удалил лишнюю задачу из плана\\! ⚡️",
        parse_mode="MarkdownV2",
        reply_markup=get_done_kb()
    )
    await state.clear()


# Колбэк на изменение состояния задачи
@plan_callback_router.callback_query(F.data == 'change_deal')
async def change_deal(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession):
    data = await get_data_by_id(session, callback.from_user.id)
    enum_deals_list = create_enum_plan(data.deals_list)
    await callback.message.edit_text(
        "<b>Продуктивность - ключ к успеху!</b> ⚡️\n\n"
        "Отправь мне <b>номер</b> задачи, состояние которой нужно изменить.\n\n"
        f"{enum_deals_list}",
        parse_mode="HTML",
        reply_markup=get_back_kb()
    )
    await state.set_state(GetChanged.choosing_changed)
    await callback.answer()


# Обработчик для изменения состояния задачи
@plan_callback_router.message(GetChanged.choosing_changed)
async def get_change_deal(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession):
    data = await get_data_by_id(session, message.from_user.id)
    data.deals_list = [(item[0], item[1:]) for item in data.deals_list.strip(")(").split("),(")]
    index = int(message.text) - 1
    deal = list(data.deals_list[index])
    deal[0] = '1' if deal[0] == '0' else '0'
    data.deals_list[index] = tuple(deal)
    data.deals_list = "),(".join(f"{state}{desc}" for state, desc in data.deals_list)
    await session.commit()
    data = await get_data_by_id(session, message.from_user.id)
    deals_list = create_beautiful_plan(data.deals_list)
    await message.answer(
        "<b>Продуктивность - ключ к успеху!</b> ⚡️\n\n"
        "А вот и ваш <b>обновленный</b> план на день!.\n\n"
        f"{deals_list}",
        parse_mode="HTML",
        reply_markup=get_done_kb()
    )
    await state.clear()


# Ежедневная функция оповещения о невыполненных задачах
async def scheduled_task(session_factory, bot, scheduler):
    async with session_factory() as session:
        users = await get_users(session)
        for user in users:
            if user.deals_list and user.notifications_state:
                run_time = datetime.now(utc) + timedelta(hours=user.timezone)
                run_time = run_time.replace(hour=0, minute=0, second=0, microsecond=0)

                if datetime.now(utc) > run_time:
                    run_time += timedelta(days=1)

                scheduler.add_job(send_message, 'date', run_date=run_time, args=[bot, session, user.user_id])


# Ежедневная функция оповещения о невыполненных задачах
async def send_message(bot, session, chat_id):
    data = await get_data_by_id(session, chat_id)
    deals_list = create_plan_for_schedules(data.deals_list)
    await bot.send_message(chat_id,
                           f"<b>Сегодня вы отлично поработали!</b> ⚡️\n\n"
                           f"Я заметил, что вы не успели выполнить некоторые задачи. Если хотите, я могу"
                           f" <b>добавить</b> их в план на текущий день.\n\n"
                           f"<b>Вот задачи, которые не были выполнены:</b>\n  {deals_list}",
                           parse_mode='HTML',
                           reply_markup=get_schedule_kb())


# Колбэк на добавление старых задач в новый список
@plan_callback_router.callback_query(F.data == 'add_plan_schedule')
async def add_old_plan(
        callback: types.CallbackQuery,
        session: AsyncSession,
        state: FSMContext):
    data = await get_data_by_id(session, callback.from_user.id)
    text = data.deals_list.split("),(")
    back_text = ''
    for elem in text:
        if bool(int(elem[0])):
            pass
        else:
            back_text += elem + "),("
    back_text = back_text[:-3]
    data.deals_list = back_text
    await session.commit()
    await callback.answer()
    await menu(callback, state)


# Колбэк на отказ от добавления старых задач в новый список
@plan_callback_router.callback_query(F.data == 'del_plan_schedule')
async def add_old_plan(
        callback: types.CallbackQuery,
        session: AsyncSession,
        state: FSMContext):
    data = await get_data_by_id(session, callback.from_user.id)
    data.deals_list = ''
    await session.commit()
    await callback.answer()
    await menu(callback, state)
