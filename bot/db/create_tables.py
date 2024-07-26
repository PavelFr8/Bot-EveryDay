from sqlalchemy.ext.asyncio import create_async_engine

from bot.db.base import Base
from bot.config_reader import config


async def create_tables():
    engine = create_async_engine(config.postgresql_url.get_secret_value(), echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
