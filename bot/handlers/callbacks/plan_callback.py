import logging

from aiogram import Router, F
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.plan_kbs import get_plan_kb, get_default_plan_kb, get_create_plan_kb, get_back_kb, get_done_kb
from bot.db.reqsts import get_data_by_id, save_data

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


def create_beautiful_plan(data: str):
    text = data.split("),(")
    back_text = ''
    for elem in text:
        if bool(int(elem[0])):
            back_text += "✅   " + f"<s>{elem[1:]}</s>" + '\n'
        else:
            back_text += "<b>•</b>  " + elem[1:] + '\n'
    return back_text


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
        session: AsyncSession):
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
    fsm_data["notifications"] = None
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