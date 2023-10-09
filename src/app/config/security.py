from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.contrib.jwt import OAuth2PasswordBearerAuth, Token
from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from app.config._settings import settings
from app.config.plugins import sqlalchemy as alchemy
from app.domain import urls
from app.domain.accounts.models import User
from app.domain.accounts.services import UserService
from app.domain.teams.models import TeamMember
from app.lib import constants

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection, Request

__all__ = ["provide_user", "current_user_from_token", "auth"]


async def provide_user(request: Request[User, Token, Any]) -> User:
    """Get the user from the connection.

    Args:
        request: current connection.

    Returns:
    User
    """
    return request.user


async def current_user_from_token(token: Token, connection: ASGIConnection[Any, Any, Any, Any]) -> User | None:
    """Lookup current user from local JWT token.

    Fetches the user information from the database


    Args:
        token (str): JWT Token Object
        connection (ASGIConnection[Any, Any, Any, Any]): ASGI connection.


    Returns:
        User: User record mapped to the JWT identifier
    """

    service = UserService(
        session=alchemy._config.provide_session(connection.app.state, connection.scope),
        statement=select(User).options(
            noload("*"),
            selectinload(User.teams).options(
                joinedload(TeamMember.team, innerjoin=True).options(
                    noload("*"),
                ),
            ),
        ),
    )
    user = await service.get_one_or_none(email=token.sub)
    return user if user and user.is_active else None


auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=current_user_from_token,
    token_secret=settings.APP_SECRET_KEY,
    token_url=urls.ACCOUNT_LOGIN,
    exclude=[
        urls.OPENAPI_SCHEMA,
        constants.SYSTEM_HEALTH,
        urls.ACCOUNT_LOGIN,
        urls.ACCOUNT_REGISTER,
    ],
)
