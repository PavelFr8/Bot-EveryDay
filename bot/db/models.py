from sqlalchemy import Column, String, Text

from bot.db.base import Base


class UserData(Base):
    __tablename__ = "user_data"

    user_id = Column(String(255), primary_key=True)
    deals_list = Column(String(1000), nullable=True)
    notification_list = Column(Text, nullable=True)
