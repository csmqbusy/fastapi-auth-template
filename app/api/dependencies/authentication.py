from fastapi import Form, Depends
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.auth.utils import (
    verify_password,
    decode_refresh_token,
    decode_access_token,
)
from app.db import get_db_session
from app.models import UserModel
from app.schemes.user import SUserSignUp
from app.services.user import get_user_by_username
from app.api.exceptions.authentication import (
    InvalidCredentialsError,
    TokenNotFoundError,
    InvalidTokenException,
    UserNotFoundError,
    UserInactiveError,
)


async def validate_credentials(
    username: str = Form(),
    password: str = Form(),
    db_session: AsyncSession = Depends(get_db_session)
):
    user = await get_user_by_username(username, db_session)
    if not user:
        raise InvalidCredentialsError()
    if not verify_password(password, user.password):
        raise InvalidCredentialsError()
    return user


async def get_refresh_token_payload(request: Request) -> dict:
    if not (refresh_token := request.cookies.get("refresh_token")):
        raise TokenNotFoundError()
    try:
        payload = decode_refresh_token(refresh_token)
    except InvalidTokenError:
        raise InvalidTokenException()
    return payload


async def get_access_token_payload(request: Request) -> dict:
    if not (access_token := request.cookies.get("access_token")):
        raise TokenNotFoundError()
    try:
        payload = decode_access_token(access_token)
    except InvalidTokenError:
        raise InvalidTokenException()
    return payload


async def get_auth_user_info(
    payload: dict = Depends(get_access_token_payload),
    db_session: AsyncSession = Depends(get_db_session),
):
    username = payload.get("sub")
    user = await get_user_by_username(username, db_session)
    if user:
        return user
    raise UserNotFoundError()


async def get_active_auth_user_info(
    user: SUserSignUp = Depends(get_auth_user_info),
):
    if user.active:
        return user
    raise UserInactiveError()


async def get_device_info(request: Request) -> SDeviceInfo:
    user_agent = request.headers.get("user-agent")
    user_ip = request.client.host if request.client else None
    return SDeviceInfo(
        user_agent=user_agent,
        ip_address=user_ip,
    )
