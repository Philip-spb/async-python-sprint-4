from typing import Optional, List

from sqlalchemy import String, Text, ForeignKey, func
from fastapi_users_db_sqlalchemy.generics import GUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase

from sqlalchemy.orm import relationship, mapped_column, Mapped

from db.db import Base, get_async_session


# https://github.com/hajime9652/task-log/blob/6ae07fad11b7713c734a4bf23278316ddbed57ce/backend_sqlite/app/db.py


# class ShortLinkTypes(enum.Enum):
#     public = 'public'
#     private = 'private'

class User(SQLAlchemyBaseUserTableUUID, Base):
    links = relationship("ShortLink", back_populates="owner", lazy=False)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class ShortLink(Base):
    __tablename__ = 'short_link'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_url: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    original_url: Mapped[str] = mapped_column(String(4096), nullable=False)
    type: Mapped[str] = mapped_column(String(100), server_default='public', nullable=False)
    owner_id: Mapped[Optional[GUID]] = mapped_column(ForeignKey('user.id'))
    owner: Mapped[Optional[User]] = relationship(User, back_populates='links', lazy=False)
    is_active: Mapped[Optional[bool]] = mapped_column(server_default='True')
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    links: Mapped[List["AccessLog"]] = relationship(lazy=False)


class AccessLog(Base):
    __tablename__ = 'access_log'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_link_id: Mapped[int] = mapped_column(ForeignKey('short_link.id'))
    connection_info: Mapped[Optional[str]] = mapped_column(Text())
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
