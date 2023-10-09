from __future__ import annotations

from pathlib import Path

from advanced_alchemy.config import AlembicAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config import SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import autocommit_before_send_handler
from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.config.response_cache import ResponseCacheConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec import Contact
from litestar.static_files.config import StaticFilesConfig

from app.config import security
from app.config._cache import cache_key_builder
from app.config._db import sqlalchemy_async_session_factory, sqlalchemy_engine
from app.config._settings import settings
from app.lib import constants
from app.lib.settings import BASE_DIR

openapi = OpenAPIConfig(
    title=settings.OPENAPI_TITLE or settings.APP_NAME,
    version=settings.OPENAPI_VERSION,
    contact=Contact(name=settings.OPENAPI_CONTACT_NAME, email=settings.OPENAPI_CONTACT_EMAIL),
    components=[security.auth.openapi_components],
    security=[security.auth.security_requirement],
    use_handler_docstrings=True,
    root_schema_site="swagger",
)
"""OpenAPI config for app.  See OpenAPISettings for configuration."""

"""Database session factory.

See [`async_sessionmaker()`][sqlalchemy.ext.asyncio.async_sessionmaker].
"""
sqlalchemy = SQLAlchemyAsyncConfig(
    session_dependency_key=constants.DB_SESSION_DEPENDENCY_KEY,
    engine_instance=sqlalchemy_engine,
    session_maker=sqlalchemy_async_session_factory,
    before_send_handler=autocommit_before_send_handler,
    alembic_config=AlembicAsyncConfig(
        version_table_name=settings.DB_MIGRATION_DDL_VERSION_TABLE,
        script_config=settings.DB_MIGRATION_CONFIG,
        script_location=settings.DB_MIGRATION_PATH,
    ),
)

csrf = CSRFConfig(
    secret=settings.APP_SECRET_KEY,
    cookie_httponly=True,
    cookie_secure=settings.APP_CSRF_COOKIE_SECURE,
    cookie_name=settings.APP_CSRF_COOKIE_NAME,
)
"""csrf config."""

cors = CORSConfig(allow_origins=settings.APP_BACKEND_CORS_ORIGINS)
"""cors config."""

compression = CompressionConfig(backend="gzip")
"""compression config."""

STATIC_DIRS = [settings.APP_STATIC_DIR]
if settings.APP_DEBUG:
    STATIC_DIRS.append(Path(BASE_DIR / "domain" / "web" / "resources"))
static_files = [
    StaticFilesConfig(
        directories=STATIC_DIRS,  # type: ignore[arg-type]
        path=settings.APP_STATIC_URL,
        name="web",
        html_mode=False,
        opt={"exclude_from_auth": True},
    ),
]
"""static files config."""

cache = ResponseCacheConfig(
    default_expiration=constants.CACHE_EXPIRATION,
    key_builder=cache_key_builder,
)
"""Cache configuration for application."""
