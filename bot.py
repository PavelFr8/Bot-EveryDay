import asyncio
from aiogram import Bot, Dispatcher

from config_reader import config

from handlers.main_menu_handler import main_menu_router


async def main():
    bot = Bot(
        token=config.bot_token.get_secret_value()
              )
    dp = Dispatcher()

    dp.include_routers(main_menu_router)

    await bot.delete_webhook(drop_pending_updates=True)
    print('bot online!')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
