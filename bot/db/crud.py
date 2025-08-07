from typing import AsyncGenerator, Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from bot import logger
from bot.db.engine import async_session
from bot.db.models import Deals, Users


async def get_users_batch_for_notify(
    batch_size: int = 100,
    last_id: Optional[int] = None,
) -> AsyncGenerator[list[Users], None]:
    try:
        async with async_session() as session:
            while True:
                query = (
                    select(Users)
                    .where(
                        and_(
                            Users.notify_state.is_(True),
                            Users.deals.any(Deals.is_done.is_(False)),
                        ),
                    )
                    .order_by(Users.id)
                    .limit(batch_size)
                )
                if last_id:
                    query = query.where(Users.id > last_id)

                result = await session.execute(query)
                users = result.unique().scalars().all()

                if not users:
                    break

                yield users
                last_id = users[-1].id
    except SQLAlchemyError as e:
        await logger.error(f"Error fetching users batch: {e}")
        yield []


async def create_user(user_id: int) -> None:
    """
    Create a new user in the database

    :param user_id: User's Telegram ID
    :return: UserData object
    """
    try:
        async with async_session() as session:
            await logger.debug(f"New user {user_id}")
            user = Users(telegram_id=user_id)
            session.add(user)
            await session.commit()
    except SQLAlchemyError as e:
        if "duplicate key value violates unique constraint" not in str(e):
            await logger.error(f"Error creating user: {e}")


async def get_user_by_id(
    user_id: int,
    session: AsyncSession | None = None,
) -> Users | None:
    """
    Get user data

    :param user_id: User's Telegram ID
    :return: UserData object (can be none if user not found)
    """
    try:
        if session is not None:
            result = await session.execute(
                select(Users).where(Users.telegram_id == user_id),
            )
            return result.unique().scalar_one_or_none()

        async with async_session() as new_session:
            result = await new_session.execute(
                select(Users).where(Users.telegram_id == user_id),
            )
            return result.unique().scalar_one_or_none()
    except SQLAlchemyError as e:
        await logger.error(f"Error getting user: {e}")
        return None


async def change_timezone(user_id: int, timezone: int) -> None:
    """
    Change user's timezone

    :param user_id: User's Telegram ID
    :param timezone: New timezone value
    """
    try:
        async with async_session() as session:
            user = await get_user_by_id(user_id, session=session)
            if user:
                user.timezone = timezone
                await session.commit()
                await logger.info(
                    f"User {user_id} timezone updated to {timezone}",
                )
            else:
                await logger.warning(
                    f"User {user_id} not found for timezone update",
                )
    except SQLAlchemyError as e:
        await logger.error(f"Error changing timezone for user {user_id}: {e}")


async def change_notify_state(user_id: int) -> None:
    """
    Change user's notification state

    :param user_id: User's Telegram ID
    :param state: New notification state
    """
    try:
        async with async_session() as session:
            user = await get_user_by_id(user_id, session=session)
            if user:
                user.notify_state = not user.notify_state
                await session.commit()
                await logger.info(
                    f"User {user_id} notify_state upd to {user.notify_state}",
                )
            else:
                await logger.warning(
                    f"User {user_id} not found for notif_state upd",
                )
    except SQLAlchemyError as e:
        await logger.error(
            f"Error changing notify state for user {user_id}: {e}",
        )


async def create_deal(user_id: int, text: str) -> None:
    """
    Create a new deal for the user

    :param user_id: User's Telegram ID
    :param text: Deal text
    """
    try:
        async with async_session() as session:
            user = await get_user_by_id(user_id, session=session)
            if user:
                deal = Deals(text=text, user=user)
                session.add(deal)
                await session.commit()
                await logger.info(f"Deal {deal.id} created")
            else:
                await logger.warning(
                    f"User {user_id} not found for deal creation",
                )
    except SQLAlchemyError as e:
        await logger.error(f"Error creating deal for user {user_id}: {e}")


async def delete_deal(user_id: int, deal_id: int) -> None:
    """
    Delete a deal by its ID

    :param deal_id: ID of the deal to delete
    """
    try:
        async with async_session() as session:
            user: Users = await get_user_by_id(user_id, session=session)
            deal: Deals = await session.get(Deals, deal_id)
            if deal in user.deals:
                await session.delete(deal)
                await session.commit()
                await logger.debug(f"Deal {deal_id} deleted")
            else:
                await logger.warning(f"Deal {deal_id} not found")
    except SQLAlchemyError as e:
        await logger.error(f"Error deleting deal {deal_id}: {e}")


async def change_deal_state(user_id: int, deal_id: int) -> None:
    """
    Change the state of a deal by its ID

    :param deal_id: ID of the deal to change state
    """
    try:
        async with async_session() as session:
            user = await get_user_by_id(user_id, session=session)
            deal = await session.get(Deals, deal_id)
            if deal in user.deals:
                deal.is_done = not deal.is_done
                await session.commit()
                await logger.debug(
                    f"Deal {deal_id} state changed to {deal.is_done}",
                )
            else:
                await logger.warning(f"Deal {deal_id} not found")
    except SQLAlchemyError as e:
        await logger.error(f"Error changing state for deal {deal_id}: {e}")
