from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user import (
    UsernameAlreadyExists,
    EmailAlreadyExists,
)
from app.models import UserModel
from app.repositories import user_repo
from app.schemes.user import SUserSignUp


async def create_user(user: SUserSignUp, session: AsyncSession) -> UserModel:
    if not (await _check_unique_username(user.username, session)):
        raise UsernameAlreadyExists
    if not (await _check_unique_email(user.email, session)):
        raise EmailAlreadyExists

    user_from_db = await user_repo.add(session, user.model_dump())
    return user_from_db


async def get_user_by_username(
    username: str,
    session: AsyncSession,
) -> UserModel | None:
    return await user_repo.get_by_filter(session, {"username": username})


async def _check_unique_username(username: str, session: AsyncSession) -> bool:
    user = await get_user_by_username(username, session)
    if user is None:
        return True
    return False


async def _check_unique_email(email: EmailStr, session: AsyncSession) -> bool:
    user = await user_repo.get_by_filter(session, {"email": email})
    if user is None:
        return True
    return False
