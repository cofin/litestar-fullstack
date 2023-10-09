from __future__ import annotations

import importlib
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Literal

from dotenv import load_dotenv
from litestar.data_extractors import RequestExtractorField, ResponseExtractorField  # noqa: TCH002
from pydantic import ValidationError, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from app import utils

__all__ = ["Settings", "load_settings"]


DEFAULT_MODULE_NAME = "app"
BASE_DIR: Final = utils.module_to_os_path(DEFAULT_MODULE_NAME)
STATIC_DIR = Path(BASE_DIR / "domain" / "web" / "public")
TEMPLATES_DIR = Path(BASE_DIR / "domain" / "web" / "templates")
version = importlib.metadata.version(DEFAULT_MODULE_NAME)


class Settings(BaseSettings):
    """Server configurations."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    SERVER_APP_LOC: str = "app.asgi:create_app"
    """Path to app executable, or factory."""
    SERVER_APP_LOC_IS_FACTORY: bool = True
    """Indicate if APP_LOC points to an executable or factory."""
    SERVER_HOST: str = "localhost"
    """Server network host."""
    SERVER_KEEPALIVE: int = 65
    """Seconds to hold connections open (65 is > AWS lb idle timeout)."""
    SERVER_PORT: int = 8000
    """Server port."""
    SERVER_RELOAD: bool | None = None
    """Turn on hot reloading."""
    SERVER_RELOAD_DIRS: list[str] = [f"{BASE_DIR}"]
    """Directories to watch for reloading."""
    SERVER_HTTP_WORKERS: int | None = None
    """Number of HTTP Worker processes to be spawned by Uvicorn."""

    """

    APP

    """

    APP_BUILD_NUMBER: str = ""
    """Identifier for CI build."""
    APP_DEBUG: bool = False
    """Run `Litestar` with `debug=True`."""
    APP_ENVIRONMENT: str = "prod"
    """'dev', 'prod', etc."""
    APP_NAME: str = "app"
    """Application name."""
    APP_SECRET_KEY: str
    """Number of HTTP Worker processes to be spawned by Uvicorn."""
    APP_JWT_ENCRYPTION_ALGORITHM: str = "HS256"
    APP_BACKEND_CORS_ORIGINS: list[str] = ["*"]
    APP_STATIC_URL: str = "/static/"
    APP_CSRF_COOKIE_NAME: str = "csrftoken"
    APP_CSRF_COOKIE_SECURE: bool = False
    """Default URL where static assets are located."""
    APP_STATIC_DIR: Path = STATIC_DIR
    APP_DEV_MODE: bool = False

    @property
    def app_slug(self) -> str:
        """Return a slugified name.

        Returns:
            `self.NAME`, all lowercase and hyphens instead of spaces.
        """
        return utils.slugify(self.APP_NAME)

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(
        cls,
        value: str | list[str],
    ) -> list[str] | str:
        """Parse a list of origins."""
        if isinstance(value, list):
            return value
        if isinstance(value, str) and not value.startswith("["):
            return [host.strip() for host in value.split(",")]
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return list(value)
        raise ValueError(value)

    @field_validator("SECRET_KEY")
    def generate_secret_key(
        cls,
        value: str | None,
    ) -> str:
        """Generate a secret key."""
        return os.urandom(32).decode() if value is None else value

    """

    LOGGING

    """
    # https://stackoverflow.com/a/1845097/6560549
    LOG_EXCLUDE_PATHS: str = r"\A(?!x)x"
    """Regex to exclude paths from logging."""
    LOG_HTTP_EVENT: str = "HTTP"
    """Log event name for logs from Litestar handlers."""
    LOG_INCLUDE_COMPRESSED_BODY: bool = False
    """Include 'body' of compressed responses in log output."""
    LOG_LEVEL: int = 20
    """Stdlib log levels.

    Only emit logs at this level, or higher.
    """
    LOG_OBFUSCATE_COOKIES: set[str] = {"session"}
    """Request cookie keys to obfuscate."""
    LOG_OBFUSCATE_HEADERS: set[str] = {"Authorization", "X-API-KEY"}
    """Request header keys to obfuscate."""
    LOG_JOB_FIELDS: list[str] = [
        "function",
        "kwargs",
        "key",
        "scheduled",
        "attempts",
        "completed",
        "queued",
        "started",
        "result",
        "error",
    ]
    """Attributes of the SAQ.

    [`Job`](https://github.com/tobymao/saq/blob/master/saq/job.py) to be
    logged.
    """
    LOG_LOG_REQUEST_FIELDS: list[RequestExtractorField] = [
        "path",
        "method",
        "headers",
        "cookies",
        "query",
        "path_params",
    ]
    """Attributes of the [Request][litestar.connection.request.Request] to be
    logged."""
    LOG_RESPONSE_FIELDS: list[ResponseExtractorField] = [
        "status_code",
        "cookies",
        "headers",
    ]
    """Attributes of the [Response][litestar.response.Response] to be
    logged."""
    LOG_WORKER_EVENT: str = "Worker"
    """Log event name for logs from SAQ worker."""
    LOG_SAQ_LEVEL: int = 20
    """Level to log SAQ logs."""
    LOG_SQLALCHEMY_LEVEL: int = 30
    """Level to log SQLAlchemy logs."""
    LOG_UVICORN_ACCESS_LEVEL: int = 30
    """Level to log uvicorn access logs."""
    LOG_UVICORN_ERROR_LEVEL: int = 20
    """Level to log uvicorn error logs."""

    """

    OPENAPI

    """
    OPENAPI_CONTACT_NAME: str = "Cody"
    """Name of contact on document."""
    OPENAPI_CONTACT_EMAIL: str = "admin"
    """Email for contact on document."""
    OPENAPI_TITLE: str | None = "Litestar Fullstack"
    """Document title."""
    OPENAPI_VERSION: str = f"v{version}"
    """Document version."""
    """

    WORKER

    """

    WORKER_CONCURRENCY: int = 10
    """The number of concurrent jobs allowed to execute per worker.

    Default is set to 10.
    """
    WORKER_WEB_ENABLED: bool = True
    """If true, the worker admin UI is launched on worker startup.."""
    """Initialization method for the worker process."""

    """

    DATABASE

    """
    DB_ECHO: bool = False
    """Enable SQLAlchemy engine logs."""
    DB_ECHO_POOL: bool | Literal["debug"] = False
    """Enable SQLAlchemy connection pool logs."""
    DB_POOL_DISABLE: bool = False
    """Disable SQLAlchemy pooling, same as setting pool to.

    [`NullPool`][sqlalchemy.pool.NullPool].
    """
    DB_POOL_MAX_OVERFLOW: int = 10
    """See [`max_overflow`][sqlalchemy.pool.QueuePool]."""
    DB_POOL_SIZE: int = 5
    """See [`pool_size`][sqlalchemy.pool.QueuePool]."""
    DB_POOL_TIMEOUT: int = 30
    """See [`timeout`][sqlalchemy.pool.QueuePool]."""
    DB_POOL_RECYCLE: int = 300
    DB_POOL_PRE_PING: bool = False
    DB_CONNECT_ARGS: dict[str, Any] = {}
    DB_URL: str = "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"
    DB_ENGINE: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_MIGRATION_CONFIG: str = f"{BASE_DIR}/config/alembic.ini"
    DB_MIGRATION_PATH: str = f"{BASE_DIR}/config/migrations"
    DB_MIGRATION_DDL_VERSION_TABLE: str = "ddl_version"

    """

    REDIS

    """
    REDIS_URL: str = "redis://localhost:6379/0"
    """A Redis connection URL."""
    REDIS_DB: int | None = None
    """Redis DB ID (optional)"""
    REDIS_PORT: int | None = None
    """Redis port (optional)"""
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    """Length of time to wait (in seconds) for a connection to become
    active."""
    REDIS_HEALTH_CHECK_INTERVAL: int = 5
    """Length of time to wait (in seconds) before testing connection health."""
    REDIS_SOCKET_KEEPALIVE: int = 5
    """Length of time to wait (in seconds) between keepalive commands."""


@lru_cache
def load_settings() -> Settings:
    """Load Settings file.

    As an example, I've commented out how you might go about injecting secrets into the environment for production.

    This fetches a `.env` configuration from a Google secret and configures the environment with those variables.

    ```python
    secret_id = os.environ.get("ENV_SECRETS", None)
    env_file_exists = os.path.isfile(f"{os.curdir}/.env")
    local_service_account_exists = os.path.isfile(f"{os.curdir}/service_account.json")
    if local_service_account_exists:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
    project_id = os.environ.get("GOOGLE_PROJECT_ID", None)
    if project_id is None:
        _, project_id = google.auth.default()
        os.environ["GOOGLE_PROJECT_ID"] = project_id
    if not env_file_exists and secret_id:
        secret = secret_manager.get_secret(project_id, secret_id)
        load_dotenv(stream=io.StringIO(secret))

    try:
        settings = ...  # existing code below
    except:
        ...
    return settings
    ```
    Returns:
        Settings: application settings
    """
    env_file = Path(f"{os.curdir}/.env")
    if env_file.is_file():
        load_dotenv(env_file)
    try:
        """Override Application reload dir."""
        settings: Settings = Settings(
            SERVER_HOST="0.0.0.0",  # noqa: S104
            SERVER_RELOAD_DIRS=[str(BASE_DIR)],
        )

    except ValidationError as e:
        print("Could not load settings.", e)  # noqa: T201
        raise
    return settings
