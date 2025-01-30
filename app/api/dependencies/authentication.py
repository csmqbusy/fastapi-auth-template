from fastapi import Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import verify_password
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
