from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request

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
    send_daily_notifications,
)
from bot.handlers.callbacks.settings_callback import settings_callback_router
from bot.handlers.menu_handler import main_menu_router
from bot.middlewares.middleware_bot import BotMiddleware
from bot.middlewares.middleware_db import DbSessionMiddleware
from bot.middlewares.middleware_scheduler import SchedulerMiddleware

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler(
    jobstores={"default": SQLAlchemyJobStore(url=config.sync_postgresql_url)},
)

# Only private chats
dp.message.filter(ChatTypeFilter(chat_type="private"))

# Middleware
dp.message.middleware(DbSessionMiddleware(async_session))
dp.callback_query.middleware(DbSessionMiddleware(async_session))
dp.callback_query.middleware(SchedulerMiddleware(scheduler))
dp.message.middleware(SchedulerMiddleware(scheduler))
dp.callback_query.middleware(BotMiddleware(bot))

# Routers
dp.include_router(main_menu_router)
dp.include_router(settings_callback_router)
dp.include_router(download_callback_router)
dp.include_router(plan_callback_router)
dp.include_router(notification_callback_router)

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = config.host_url.get_secret_value() + "/webhook"
    await bot.set_webhook(webhook_url)
    scheduler.add_job(
        send_daily_notifications,
        "cron",
        hour=0,
        minute=0,
        id="daily_schedule",
        replace_existing=True,
    )
    scheduler.start()
    await logger.info("Bot is up")


@app.on_event("shutdown")
async def on_shutdown():
    await logger.info("Shutting down...")
    await bot.session.close()
    await engine.dispose()
    scheduler.shutdown()
    await logger.shutdown()
