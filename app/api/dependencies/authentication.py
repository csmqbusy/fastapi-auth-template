from fastapi import Form, Depends, HTTPException
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from app.auth.utils import (
    verify_password,
    decode_refresh_token,
    decode_access_token,
)
from app.db import get_db_session
from app.services.user_service import get_user_by_username
from app.api.exceptions.authentication import InvalidCredentialsException


async def validate_credentials(
    username: str = Form(),
    password: str = Form(),
    db_session: AsyncSession = Depends(get_db_session)
):
    user = await get_user_by_username(username, db_session)
    if not user:
        raise InvalidCredentialsException()
    if not verify_password(password, user.password):
        raise InvalidCredentialsException()
    return user


async def get_refresh_token_payload(request: Request) -> dict:
    if not (refresh_token := request.cookies.get("refresh_token")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found.",
        )
    try:
        payload = decode_refresh_token(refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )
    return payload


async def get_access_token_payload(request: Request) -> dict:
    if not (access_token := request.cookies.get("access_token")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found.",
        )
    try:
        payload = decode_access_token(access_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )
    return payload

