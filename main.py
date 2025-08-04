import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    setup_application,
    SimpleRequestHandler,
)
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot import logger
from bot.config_reader import config
from bot.db.engine import async_session, engine
from bot.filters.chat_type import ChatTypeFilter
from bot.handlers.callbacks.download_callback import download_callback_router
from bot.handlers.callbacks.notification_callback import (
    notification_callback_router,
)
from bot.handlers.callbacks.plan_callback import (
    plan_callback_router,
    scheduled_task,
)
from bot.handlers.callbacks.settings_callback import settings_callback_router
from bot.handlers.menu_handler import main_menu_router
from bot.middlewares.middleware_bot import BotMiddleware
from bot.middlewares.middleware_db import DbSessionMiddleware
from bot.middlewares.middleware_scheduler import SchedulerMiddleware

# TODO: refactor main.py


async def main(url: str):
    logger.info("Starting bot...")

    # Creating bot and its dispatcher
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    scheduler = AsyncIOScheduler()

    # Bot works only in private chats
    dp.message.filter(ChatTypeFilter(chat_type="private"))

    # Register middlewares
    dp.message.middleware(DbSessionMiddleware(async_session))
    dp.callback_query.middleware(DbSessionMiddleware(async_session))
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
    scheduler.add_job(
        scheduled_task,
        "cron",
        hour=0,
        minute=0,
        args=[async_session, bot, scheduler],
    )

    # Delete existing webhook and set a new one
    logger.info("Setting webhook...")
    await bot.delete_webhook(drop_pending_updates=True)

    # Use ngrok URL for webhook
    host_url = url
    webhook_url = f"{host_url}/webhook"
    await bot.set_webhook(webhook_url)

    logger.info("Bot online!")
    scheduler.start()

    # Start the HTTP server
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        "127.0.0.1",
        8080,
    )  # Bind to port 8080 or the port your hosting provider supports
    await site.start()

    try:
        await asyncio.Event().wait()  # Keep the service running
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up...")
        await bot.session.close()
        await engine.dispose()
        await runner.cleanup()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: \npython3 main.py <url> - run bot")
        sys.exit(1)

    url = sys.argv[1]
    asyncio.run(main(url))
