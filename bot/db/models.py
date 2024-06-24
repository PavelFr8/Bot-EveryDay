from sqlalchemy import Column, BigInteger, String

from bot.db.base import Base


class UserData(Base):
    __tablename__ = "user_data"

    user_id = Column(BigInteger, primary_key=True)
    deals_list = Column(String(65535), nullable=True)
    notification_list = Column(String(65535), nullable=False)

