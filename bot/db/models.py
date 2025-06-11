from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base


class Users(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer(), index=True, unique=True, nullable=False,)
    timezone: Mapped[int] = mapped_column(Integer(), default=3)
    notify_state: Mapped[bool] = mapped_column(Boolean(), default=True)
    notifications: Mapped[list["Notifications"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    deals: Mapped[list["Deals"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Notifications(Base):
    __tablename__ = "notifications"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    user: Mapped["Users"] = relationship(back_populates="notifications")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Deals(Base):
    __tablename__ = "deals"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    user: Mapped["Users"] = relationship(back_populates="deals")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
