from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Text, create_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)
from sqlalchemy.schema import MetaData
from sqlalchemy.sql import func

engine = create_engine("sqlite:///go-ji.db")
# engine = create_engine("sqlite:///:memory:")
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
Base.query = db_session.query_property()

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
Base.metadata = MetaData(naming_convention=convention)


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

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())


def init_db():
    Base.metadata.create_all(bind=engine)
