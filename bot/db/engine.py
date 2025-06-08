from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config_reader import config

DATABASE_URL = config.postgresql_url.get_secret_value()


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
