from typing import Dict

from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.ext.asyncio import AsyncSession

from bot.cbdata import MenuCallbackFactory
from bot.keyboards.notification_kb import get_default_notification_kb, get_back_kb, get_time_kb, get_done_kb
from bot.db.reqsts import get_data_by_id, save_data


notification_callback_router = Router()


# Класс для диалога про добавление нового напоминания
class GetNotification(StatesGroup):
    getting_name = State()
    getting_time = State()


async def new_notification(
        data: Dict,
        bot: Bot,
        session: AsyncSession):
    notification = data["notifications"][2:]
    message: types.Message = data["message"]
    reminder_text = f"📅  У вас новое <b>напоминание</b>:\n\n<i>{notification}</i>\n\nЯ всегда рад вам помочь! 🌟"

    await bot.send_message(message.from_user.id,
                           reminder_text,
                           parse_mode="HTML")

    tmp_data = await get_data_by_id(session, message.from_user.id)
    tmp_data.notification_list = tmp_data.notification_list.replace(data["notifications"], '')
    tmp_data.notification_list = tmp_data.notification_list.replace("),(),(", '),(')
    if tmp_data.notification_list == '),(':
        tmp_data.notification_list = ''
    tmp_data.notification_list = tmp_data.notification_list.strip()
    if tmp_data.notification_list[-3:] == '),(':
        tmp_data.notification_list = tmp_data.notification_list[:-3]
    await session.commit()


def create_beautiful_notifications(notf_list):
    data = notf_list.split("),(")
    data_list = ''
    for elem in data:
        time = elem[:2]
        if time == '60':
            time = '1 час'
        elif time == '05':
            time = '5 минут'
        else:
            time = f'{time} минут'
        data_list += "• " + elem[2:] + f" (Режим: {time})" + "\n"
    return data_list


# Колбэк для напоминаний
@notification_callback_router.callback_query(F.data == "back_notification")
@notification_callback_router.callback_query(MenuCallbackFactory.filter(F.action == "reminder"))
async def callback_reminder(
        callback: types.CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    data = await get_data_by_id(session, callback.from_user.id)
    if data.notification_list:
        data_list = create_beautiful_notifications(data.notification_list)
        await callback.message.edit_text(
            '🔔  Нужно напоминание? <b>Не проблема</b>! \n\nДобавьте новое напоминание, '
            'и я прослежу, чтобы вы не пропустили ничего важного\\. Ваш личный органайзер <b>всегда под рукой</b>! \n\n'
            f'А вот и список текущих напоминаний:\n{data_list}',
            parse_mode="HTML",
            reply_markup=get_default_notification_kb()
        )
    else:
        await callback.message.edit_text(
            '🔔  Нужно напоминание\\? *Не проблема\\!* \n\nДобавьте новое напоминание, '
            'и я прослежу, чтобы вы не пропустили ничего важного\\. Ваш личный органайзер *всегда под рукой*\\!',
            parse_mode="MarkdownV2",
            reply_markup=get_default_notification_kb()
        )
    await state.clear()


# Колбэк на создание имени для уведомления
@notification_callback_router.callback_query(F.data == 'add_notification')
async def add_notification(
        callback: types.CallbackQuery,
        state: FSMContext):
    await callback.message.edit_text(
        "*Давайте создадим напоминание\\!* 🔔\n\n"
        "Отправь мне *сообщение*, которое будет названием напоминания, а дальше я помогу тебе выбрать время\\.\n\n"
        "*Пример сообщения: _Сходить в магазин_*",
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    fsm_data = await state.get_data()
    fsm_data["message"] = callback.message
    await state.set_data(fsm_data)
    await state.set_state(GetNotification.getting_name)
    await callback.answer()


# Обработчик для добавления нового уведомления
@notification_callback_router.message(GetNotification.getting_name)
async def add_deal(
        message: types.Message,
        state: FSMContext):
    fsm_data = await state.get_data()
    fsm_data["deals"] = ''
    fsm_data["notifications"] = message.text
    old_message = fsm_data["message"]
    await state.set_data(fsm_data)
    await old_message.edit_text(
        "*Отлично\\!* \nПерейдем к следующему шагу\\!",
        parse_mode="MarkdownV2",
        reply_markup=get_back_kb()
    )
    await message.answer(
        text='🔔  *Выберите через сколько минут мне отправить напоминание*',
        parse_mode="MarkdownV2",
        reply_markup=get_time_kb()
    )
    await state.set_state(GetNotification.getting_time)


# Обработчик для добавления времени для нового уведомления
@notification_callback_router.message(GetNotification.getting_time)
async def add_time(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
        scheduler: AsyncIOScheduler,
        bot: Bot):
    fsm_data = await state.get_data()

    text = message.text.split('Через ')[1][:2]
    if text == '1 ':
        text = '60'
    if text == '5 ':
        text = '05'
    fsm_data["notifications"] = text + fsm_data["notifications"]

    await save_data(session, message.from_user.id, fsm_data)
    await message.answer(
        text="*Отлично\\!* \nЯ добавил новое уведомление\\!  🔔",
        parse_mode="MarkdownV2",
        reply_markup=get_done_kb()
    )
    fsm_data["message"] = message
    if text == '05':
        text = 5
    run_time = datetime.now() + timedelta(minutes=int(text))
    scheduler.add_job(new_notification, 'date', run_date=run_time, args=[fsm_data, bot, session])
    await state.set_state(GetNotification.getting_time)
