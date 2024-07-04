import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select

from bot.config_reader import config
from bot.handlers.menu_handler import main_menu_router
from bot.handlers.menu_callbacks import menu_callback_router
from bot.handlers.callbacks.download_callback import download_callback_router
from bot.handlers.callbacks.plan_callback import plan_callback_router
from bot.handlers.callbacks.notification_callback import notification_callback_router
from bot.filters.chat_type import ChatTypeFilter
from bot.middlewares.middleware_db import DbSessionMiddleware
from bot.handlers.callbacks.plan_callback import scheduled_task


async def main():
    # Run logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    # Creating DB engine for MySQL
    engine = create_async_engine(config.mysql_url.get_secret_value(), echo=True)
    db_pool = sessionmaker(engine, future=True, expire_on_commit=False, class_=AsyncSession)

    from bot.db.base import Base
    from bot.db.models import UserData

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    '''
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = await session.execute(select(UserData))
            all_data = result.scalars().all()
            for data in all_data:
                print(f"User ID: {data.user_id}")
                print(f"Deals List: {data.deals_list}")
                print(f"Notification List: {data.notification_list}")
    '''
    async def clear_table(table_class):
        async with engine.begin() as conn:
            await conn.run_sync(lambda conn: conn.execute(table_class.__table__.delete()))

    # await clear_table(UserData)
    # await create_tables()
    # Creating DB connections pool

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    # Bot work only in private chats
    dp.message.filter(ChatTypeFilter(chat_type="private"))

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))

    dp.include_routers(main_menu_router)
    dp.include_routers(menu_callback_router)
    dp.include_routers(download_callback_router)
    dp.include_routers(plan_callback_router)
    dp.include_routers(notification_callback_router)

    scheduler = AsyncIOScheduler()

    # scheduler.add_job(scheduled_task, 'interval', seconds=10, args=[db_pool, bot])
    scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0, args=[db_pool, bot])

    try:
        scheduler.start()
        logging.info('Bot online!')
        # Work with all requests to bot and run bot
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logging.info('Bot stop!')
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
