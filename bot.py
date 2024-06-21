import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import config
from handlers.menu_handler import main_menu_router
from handlers.menu_callbacks import menu_callback_router
from handlers.download_callback import download_callback_router
from filters.chat_type import ChatTypeFilter


# Включаем логирование.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


async def main():
    bot = Bot(token=config.bot_token.get_secret_value())

    dp = Dispatcher(storage=MemoryStorage())

    # Бот работает только в личных сообщениях.
    dp.message.filter(ChatTypeFilter(chat_type="private"))

    dp.include_routers(main_menu_router)
    dp.include_routers(menu_callback_router)
    dp.include_routers(download_callback_router)

    try:
        logging.info('Bot online!')
        # Обрабатываем все скопившиеся запросы и запускаем бота.
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logging.info('Bot stop!')
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
