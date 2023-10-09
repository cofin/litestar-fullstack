from __future__ import annotations

from typing import TYPE_CHECKING

from app.config import plugins, security
from app.config._cache import cache_key_builder, redis, redis_store_factory
from app.config._db import get_db_session
from app.config._env import cache, compression, cors, csrf, openapi, sqlalchemy, static_files
from app.config._logs import get_logger, logs
from app.config._settings import settings

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from advanced_alchemy.extensions.litestar.plugins import SQLAlchemyPlugin
    from litestar import Request
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    "plugins",
    "security",
    "openapi",
    "sqlalchemy",
    "cache",
    "cors",
    "compression",
    "csrf",
    "static_files",
    "settings",
    "logs",
    "get_logger",
    "cache_key_builder",
    "redis",
    "redis_store_factory",
    "get_db_session",
)
