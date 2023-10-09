from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config._settings import settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncSession


sqlalchemy_engine = create_async_engine(
    settings.DB_URL,
    future=True,
    echo=settings.DB_ECHO,
    echo_pool=True if settings.DB_ECHO_POOL == "debug" else settings.DB_ECHO_POOL,
    max_overflow=settings.DB_POOL_MAX_OVERFLOW,
    pool_size=settings.DB_POOL_SIZE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_use_lifo=True,  # use lifo to reduce the number of idle connections
    poolclass=NullPool if settings.DB_POOL_DISABLE else None,
    connect_args=settings.DB_CONNECT_ARGS,
)
sqlalchemy_async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    sqlalchemy_engine,
    expire_on_commit=False,
)
"""Database session factory.

See [`async_sessionmaker()`][sqlalchemy.ext.asyncio.async_sessionmaker].
"""


@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Use this to get a database session where you can't in litestar.

    Returns:
        AsyncIterator[AsyncSession]
    """
    async with sqlalchemy_async_session_factory() as session:
        yield session
