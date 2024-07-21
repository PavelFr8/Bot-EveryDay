import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiohttp import web

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from config_reader import config
from handlers.menu_handler import main_menu_router
from handlers.callbacks.settings_callback import settings_callback_router
from handlers.callbacks.download_callback import download_callback_router
from handlers.callbacks.plan_callback import plan_callback_router, scheduled_task
from handlers.callbacks.notification_callback import notification_callback_router
from middlewares.middleware_db import DbSessionMiddleware
from middlewares.middleware_scheduler import SchedulerMiddleware
from middlewares.middleware_bot import BotMiddleware
from filters.chat_type import ChatTypeFilter


async def start_http_server():
    async def handle(request):
        return web.Response(text="Bot is running")

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  # Bind to port 8080
    await site.start()
    logging.info("HTTP server started on port 8080")


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Creating DB engine for PostgreSQL
    engine = create_async_engine(config.mysql_url.get_secret_value(), echo=True)
    db_pool = sessionmaker(engine, future=True, expire_on_commit=False, class_=AsyncSession)

    # Uncomment to create tables if they don't exist
    '''
    from db.base import Base
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    await create_tables()
    '''

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    scheduler = AsyncIOScheduler()

    # Bot works only in private chats
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

    # Start the HTTP server
    await start_http_server()

    try:
        logging.info('Bot online!')
        # Work with all requests to bot and run bot
        scheduler.start()
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except (KeyboardInterrupt, SystemExit):
        logging.warning('Bot stopped!')
    except Exception as e:
        logging.error(f'Unexpected error: {e}', exc_info=True)
    finally:
        await bot.session.close()
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())