from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from go_ji.db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(Text(), nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())


class Short(Base):
    __tablename__ = "shorts"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(Text(), nullable=False, unique=True)
    longs: Mapped[List["Long"]] = relationship(back_populates="short")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())


class Long(Base):
    __tablename__ = "longs"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text(), nullable=False)
    short_id: Mapped[int] = mapped_column(ForeignKey("shorts.id"), nullable=False)
    short: Mapped["Short"] = relationship(back_populates="longs")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
