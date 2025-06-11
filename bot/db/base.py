from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )
