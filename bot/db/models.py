from sqlalchemy import Boolean, Column, Integer, String, Text

from bot.db.base import Base


class UserData(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True)
    deals_list = Column(String(1000), nullable=True)
    notification_list = Column(Text, nullable=True)
    timezone = Column(Integer(), nullable=True, default=0)
    notifications_state = Column(Boolean(), nullable=False, default=True)
