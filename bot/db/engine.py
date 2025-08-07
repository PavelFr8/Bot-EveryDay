from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config_reader import config


engine = create_async_engine(config.async_postgresql_url, echo=False)
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
