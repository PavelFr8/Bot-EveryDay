import asyncio

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from bot.config_reader import config
from bot.handlers.menu_handler import main_menu_router
from bot.handlers.callbacks.settings_callback import settings_callback_router
from bot.handlers.callbacks.download_callback import download_callback_router
from bot.handlers.callbacks.plan_callback import plan_callback_router, scheduled_task
from bot.handlers.callbacks.notification_callback import notification_callback_router
from bot.middlewares.middleware_db import DbSessionMiddleware
from bot.middlewares.middleware_scheduler import SchedulerMiddleware
from bot.middlewares.middleware_bot import BotMiddleware
from bot.filters.chat_type import ChatTypeFilter
from bot import logger


async def main():
    # Creating DB engine for PostgreSQL
    engine = create_async_engine(config.mysql_url.get_secret_value(), echo=True)
    db_pool = sessionmaker(engine, future=True, expire_on_commit=False, class_=AsyncSession)

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
    dp.include_router(main_menu_router)
    dp.include_router(settings_callback_router)
    dp.include_router(download_callback_router)
    dp.include_router(plan_callback_router)
    dp.include_router(notification_callback_router)

    # Register job in scheduler
    scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0, args=[db_pool, bot, scheduler])

    # Delete existing webhook and set a new one
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = f"https://bot-everyday.onrender.com/webhook"  # Replace with your domain
    await bot.set_webhook(webhook_url)

    await logger.info('Bot online!')
    scheduler.start()

    # Start the HTTP server
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path='/webhook')
    setup_application(app, dp, bot=bot)

    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  # Bind to port 8080 or the port your hosting provider supports
    await site.start()

    try:
        await asyncio.Event().wait()  # Keep the service running
    except (KeyboardInterrupt, SystemExit):
        await logger.warning('Bot stopped!')
    except Exception as e:
        await logger.error(f'Unexpected error: {e}', exc_info=True)
    finally:
        await bot.session.close()
        await engine.dispose()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
