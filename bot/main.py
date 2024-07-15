import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from bot.config_reader import config
from bot.handlers.menu_handler import main_menu_router
from bot.handlers.callbacks.settings_callback import settings_callback_router
from bot.handlers.callbacks.download_callback import download_callback_router
from bot.handlers.callbacks.plan_callback import plan_callback_router
from bot.handlers.callbacks.notification_callback import notification_callback_router
from bot.handlers.callbacks.plan_callback import scheduled_task
from bot.middlewares.middleware_db import DbSessionMiddleware
from bot.middlewares.middleware_scheduler import SchedulerMiddleware
from bot.middlewares.middleware_bot import BotMiddleware
from bot.filters.chat_type import ChatTypeFilter


async def main():
    # Run logging
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Creating DB engine for MySQL
    engine = create_async_engine(config.mysql_url.get_secret_value(), echo=True)
    db_pool = sessionmaker(engine, future=True, expire_on_commit=False, class_=AsyncSession)

    '''
    from bot.db.base import Base

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # await create_tables()
    '''

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    scheduler = AsyncIOScheduler()

    # Bot work only in private chats
    dp.message.filter(ChatTypeFilter(chat_type="private"))

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(DbSessionMiddleware(db_pool))
    dp.callback_query.middleware(SchedulerMiddleware(scheduler))
    dp.message.middleware(SchedulerMiddleware(scheduler))
    dp.callback_query.middleware(BotMiddleware(bot))

    # Register routers
    dp.include_routers(main_menu_router)
    dp.include_routers(settings_callback_router)
    dp.include_routers(download_callback_router)
    dp.include_routers(plan_callback_router)
    dp.include_routers(notification_callback_router)

    # Register job in scheduler
    scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0, args=[db_pool, bot, scheduler])

    try:
        logging.info('Bot online!')
        # Work with all requests to bot and run bot
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logging.info('Bot stop!')
        await bot.session.close()


asyncio.run(main())
