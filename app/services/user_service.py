from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import (
    UsernameAlreadyExists,
    EmailAlreadyExists,
)
from app.models import UserModel
from app.repositories.user import get_user_by_params, add_user
from app.schemas.user import SUserSignUp


async def create_user(user: SUserSignUp, session: AsyncSession) -> None:
    if not (await _check_unique_username(user.username, session)):
        raise UsernameAlreadyExists
    if not (await _check_unique_email(user.email, session)):
        raise EmailAlreadyExists

    await add_user(user, session)


async def get_user_by_username(
    username: str,
    session: AsyncSession,
) -> UserModel | None:
    return await get_user_by_params(session, {"username": username})


async def _check_unique_username(username: str, session: AsyncSession) -> bool:
    user = await get_user_by_username(username, session)
    if user is None:
        return True
    return False


async def _check_unique_email(email: EmailStr, session: AsyncSession) -> bool:
    user = await get_user_by_params(session, {"email": email})
    if user is None:
        return True
    return False
