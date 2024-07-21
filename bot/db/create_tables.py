from sqlalchemy.ext.asyncio import create_async_engine

from base import Base
from bot.config_reader import config

engine = create_async_engine(config.mysql_url.get_secret_value(), echo=True)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    create_tables()
