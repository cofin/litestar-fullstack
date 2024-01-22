from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.security.jwt import OAuth2PasswordBearerAuth, Token
from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from app.config.app import alchemy
from app.config.base import get_settings
from app.db.models import TeamMember, User
from app.domain import urls
from app.domain.accounts.services import UserService
from app.domain.system.urls import SYSTEM_HEALTH

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection, Request

settings = get_settings()


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

    async with UserService.new(
        session=alchemy.provide_session(connection.app.state, connection.scope),
        statement=select(User).options(
            noload("*"),
            selectinload(User.teams).options(
                joinedload(TeamMember.team, innerjoin=True).options(
                    noload("*"),
                ),
            ),
        ),
    ) as service:
        user = await service.get_one_or_none(email=token.sub)
        if user and user.is_active:
            return user
    return None


auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=current_user_from_token,
    token_secret=settings.app.SECRET_KEY,
    token_url=urls.ACCOUNT_LOGIN,
    exclude=[
        urls.OPENAPI_SCHEMA,
        SYSTEM_HEALTH,
        urls.ACCOUNT_LOGIN,
        urls.ACCOUNT_REGISTER,
    ],
)
