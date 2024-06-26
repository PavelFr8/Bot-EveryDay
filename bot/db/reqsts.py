from typing import Dict

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import UserData


async def get_data_by_id(session: AsyncSession, user_id: int) -> UserData:
    """
    Get user data

    :param session: SQLAlchemy DB session
    :param user_id: User's Telegram ID
    :return: UserData object (can be empty)
    """
    data_request = await session.execute(
        select(UserData).where(UserData.user_id == user_id)
    )
    return data_request.scalars().first()


async def save_data(session: AsyncSession, user_id: int, data: Dict = None):
    """
    Send updated data to db

    :param session: SQLAlchemy DB session
    :param data: user data dictionary
    :param user_id: User's Telegram ID
    """
    user = await session.execute(
        select(UserData).where(UserData.user_id == user_id)
    )
    user = user.scalars().first()
    if bool(user):
        logging.info(f'Update user {user_id}')
        if data:
            if user.deals_list:
                user.deals_list = user.deals_list + "),(" + '0' + f'{data["deals"]}'
            else:
                user.deals_list = '0' + f'{data["deals"]}'
            if user.notification_list:
                user.notification_list = user.notification_list + data['notifications']

    else:
        logging.info(f'New user {user_id}')
        entry = UserData()
        entry.user_id = user_id
        if data:
            if data['deals']:
                entry.deals_list = data['deals']
            else:
                entry.deals_list = ''
            if data['notifications']:
                entry.notification_list = data['notifications']
            else:
                entry.notification_list = ''
        else:
            entry.deals_list = ''
            entry.notification_list = ''
        session.add(entry)
    await session.commit()
    logging.info('Func save_data() stop work')
