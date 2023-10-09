# pylint: disable=[invalid-name,import-outside-toplevel]
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from litestar import Litestar


__all__ = ["create_app"]


def create_app() -> Litestar:
    """Create ASGI application."""

    from litestar import Litestar
    from litestar.config.app import ExperimentalFeatures
    from litestar.di import Provide
    from litestar.stores.registry import StoreRegistry

    from app import config, domain
    from app.config import plugins, security, settings
    from app.lib import (
        constants,
        exceptions,
        log,
        repository,
    )
    from app.lib.dependencies import create_collection_dependencies

    dependencies = {constants.USER_DEPENDENCY_KEY: Provide(security.provide_user)}
    dependencies.update(create_collection_dependencies())

    return Litestar(
        response_cache_config=config.cache,
        stores=StoreRegistry(default_factory=config.redis_store_factory),
        cors_config=config.cors,
        dependencies=dependencies,
        exception_handlers={
            exceptions.ApplicationError: exceptions.exception_to_http_response,  # type: ignore[dict-item]
        },
        debug=settings.APP_DEBUG,
        before_send=[log.controller.BeforeSendHandler()],
        middleware=[log.controller.middleware_factory],
        logging_config=config.logs,
        openapi_config=config.openapi,
        route_handlers=[*domain.routes],
        plugins=[
            plugins.sqlalchemy,
            plugins.aiosql,
            plugins.vite,
            plugins.saq,
            plugins.pydantic,
        ],
        on_shutdown=[config.redis.aclose],
        on_startup=[lambda: log.configure(log.default_processors)],  # type: ignore[arg-type]
        on_app_init=[security.auth.on_app_init, repository.on_app_init],
        static_files_config=config.static_files,
        signature_namespace=domain.signature_namespace,
        experimental_features=[ExperimentalFeatures.DTO_CODEGEN],
    )
